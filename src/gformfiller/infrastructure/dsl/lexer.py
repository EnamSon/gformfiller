# infrastructure/dsl/lexer.py

from typing import List, Optional
from .tokens import Token, TokenType
from .exceptions import LexerError


class Lexer:
    r"""
    Tokenize DSL expressions with escape character support
    
    Supported escape sequences:
        \\    -> \
        \&    -> &
        \|    -> |
        \~    -> ~
        \<    -> <
        \(    -> (
        \)    -> )
        \     -> (space)
    """
    
    def __init__(self, input_text: str):
        self.input = input_text
        self.position = 0
        self.current_char: Optional[str] = input_text[0] if input_text else None
    
    def error(self, message: str) -> LexerError:
        """Raise lexer error with position"""
        return LexerError(
            message=message,
            position=self.position,
            context=self._get_context()
        )
    
    def _get_context(self, window: int = 10) -> str:
        """Get context around current position for error messages"""
        start = max(0, self.position - window)
        end = min(len(self.input), self.position + window)
        context = self.input[start:end]
        pointer = " " * (self.position - start) + "^"
        return f"{context}\n{pointer}"
    
    def advance(self) -> None:
        """Move to next character"""
        self.position += 1
        if self.position >= len(self.input):
            self.current_char = None
        else:
            self.current_char = self.input[self.position]
    
    def peek(self, offset: int = 1) -> Optional[str]:
        """Look ahead without advancing"""
        peek_pos = self.position + offset
        if peek_pos >= len(self.input):
            return None
        return self.input[peek_pos]
    
    def skip_whitespace(self) -> None:
        """Skip whitespace characters"""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
    
    def read_word(self) -> Token:
        r"""
        Read a word, handling escape sequences
        
        A word is a sequence of characters that can include:
        - Letters, digits, underscores
        - Escaped special characters (\\, \&, \|, etc.)
        - Escaped spaces (\ )
        
        Examples:
            abc          -> "abc"
            user\&admin  -> "user&admin"
            first\ name  -> "first name"
            path\\file   -> "path\file"
        """
        start_pos = self.position
        result = []
        
        while self.current_char is not None:
            # Handle escape sequences
            if self.current_char == '\\':
                self.advance()  # Skip backslash
                
                if self.current_char is None:
                    raise self.error("Unexpected end of input after backslash")
                
                # Add the escaped character literally
                result.append(self.current_char)
                self.advance()
            
            # Stop at unescaped special characters
            elif self.current_char in '&|~<()':
                break
            
            # Stop at unescaped whitespace
            elif self.current_char.isspace():
                break
            
            # Regular character
            else:
                result.append(self.current_char)
                self.advance()
        
        if not result:
            raise self.error("Expected word")
        
        word = ''.join(result)
        length = self.position - start_pos
        
        return Token(
            type=TokenType.WORD,
            value=word,
            position=start_pos,
            length=length
        )
    
    def read_quoted_string(self, quote_char: str) -> Token:
        """
        Read a quoted string (single or double quotes)
        
        Examples:
            "hello world"  -> "hello world"
            'user&admin'   -> "user&admin"
            "she said \"hi\""  -> "she said "hi""
        """
        start_pos = self.position
        self.advance()  # Skip opening quote
        
        result = []
        
        while self.current_char is not None:
            # Handle escape sequences in quoted strings
            if self.current_char == '\\':
                self.advance()
                
                if self.current_char is None:
                    raise self.error("Unexpected end of input in quoted string")
                
                # Handle common escape sequences
                if self.current_char == 'n':
                    result.append('\n')
                elif self.current_char == 't':
                    result.append('\t')
                elif self.current_char == '\\':
                    result.append('\\')
                elif self.current_char == quote_char:
                    result.append(quote_char)
                else:
                    # Unknown escape - include literally
                    result.append(self.current_char)
                
                self.advance()
            
            # End of quoted string
            elif self.current_char == quote_char:
                self.advance()  # Skip closing quote
                break
            
            # Regular character in quoted string
            else:
                result.append(self.current_char)
                self.advance()
        else:
            raise self.error(f"Unterminated quoted string (expected {quote_char})")
        
        string_value = ''.join(result)
        length = self.position - start_pos
        
        return Token(
            type=TokenType.QUOTED_STRING,
            value=string_value,
            position=start_pos,
            length=length
        )
    
    def tokenize(self) -> List[Token]:
        """
        Tokenize the entire input
        
        Returns:
            List of tokens
            
        Raises:
            LexerError: If invalid syntax is encountered
        """
        tokens = []
        
        while self.current_char is not None:
            # Skip whitespace
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # Single character operators
            if self.current_char == '&':
                tokens.append(Token(TokenType.AND, '&', self.position, 1))
                self.advance()
            
            elif self.current_char == '|':
                tokens.append(Token(TokenType.OR, '|', self.position, 1))
                self.advance()
            
            elif self.current_char == '~':
                tokens.append(Token(TokenType.NOT, '~', self.position, 1))
                self.advance()
            
            elif self.current_char == '<':
                tokens.append(Token(TokenType.BEFORE, '<', self.position, 1))
                self.advance()
            
            elif self.current_char == '(':
                tokens.append(Token(TokenType.LPAREN, '(', self.position, 1))
                self.advance()
            
            elif self.current_char == ')':
                tokens.append(Token(TokenType.RPAREN, ')', self.position, 1))
                self.advance()
            
            # Quoted strings
            elif self.current_char in ('"', "'"):
                quote_char = self.current_char
                tokens.append(self.read_quoted_string(quote_char))
            
            # Words (including escaped characters)
            else:
                tokens.append(self.read_word())
        
        # Add EOF token
        tokens.append(Token(TokenType.EOF, None, self.position, 0))
        
        return tokens