# tests/unit/infrastructure/dsl/test_lexer.py

import pytest
from gformfiller.infrastructure.dsl.lexer import Lexer
from gformfiller.infrastructure.dsl.tokens import TokenType
from gformfiller.infrastructure.dsl.exceptions import LexerError


class TestLexerEscaping:
    """Tests for escape sequence handling in lexer"""
    
    def test_escape_ampersand(self):
        """Test escaping & character"""
        lexer = Lexer(r"user\&admin")
        tokens = lexer.tokenize()
        
        assert len(tokens) == 2  # WORD + EOF
        assert tokens[0].type == TokenType.WORD
        assert tokens[0].value == "user&admin"
    
    def test_escape_pipe(self):
        """Test escaping | character"""
        lexer = Lexer(r"name\|surname")
        tokens = lexer.tokenize()
        
        assert tokens[0].value == "name|surname"
    
    def test_escape_space(self):
        """Test escaping space for multi-word terms"""
        lexer = Lexer(r"first\ name")
        tokens = lexer.tokenize()
        
        assert len(tokens) == 2  # WORD + EOF
        assert tokens[0].value == "first name"
    
    def test_escape_multiple_spaces(self):
        """Test escaping multiple spaces"""
        lexer = Lexer(r"date\ of\ birth")
        tokens = lexer.tokenize()
        
        assert tokens[0].value == "date of birth"
    
    def test_escape_backslash(self):
        """Test escaping backslash itself"""
        lexer = Lexer(r"path\\to\\file")
        tokens = lexer.tokenize()
        
        assert tokens[0].value == r"path\to\file"
    
    def test_escape_tilde(self):
        """Test escaping ~ character"""
        lexer = Lexer(r"\~important")
        tokens = lexer.tokenize()
        
        assert tokens[0].value == "~important"
    
    def test_escape_less_than(self):
        """Test escaping < character"""
        lexer = Lexer(r"3\<5")
        tokens = lexer.tokenize()
        
        assert tokens[0].value == "3<5"
    
    def test_escape_parentheses(self):
        """Test escaping parentheses"""
        lexer = Lexer(r"\(optional\)")
        tokens = lexer.tokenize()
        
        assert tokens[0].value == "(optional)"
    
    def test_mixed_escaped_and_normal(self):
        """Test mixing escaped and normal characters"""
        lexer = Lexer(r"abc\&def xyz")
        tokens = lexer.tokenize()
        
        assert len(tokens) == 3  # WORD + WORD + EOF
        assert tokens[0].value == "abc&def"
        assert tokens[1].value == "xyz"
    
    def test_escape_at_end(self):
        """Test backslash at end of input raises error"""
        lexer = Lexer("word\\")
        
        with pytest.raises(LexerError) as exc_info:
            lexer.tokenize()
        
        assert "after backslash" in str(exc_info.value).lower()
    
    def test_complex_expression_with_escaping(self):
        """Test complex expression with multiple escape sequences"""
        lexer = Lexer(r"first\ name & user\&admin")
        tokens = lexer.tokenize()
        
        assert len(tokens) == 4  # WORD + AND + WORD + EOF
        assert tokens[0].value == "first name"
        assert tokens[1].type == TokenType.AND
        assert tokens[2].value == "user&admin"


class TestLexerQuotedStrings:
    """Tests for quoted string handling"""
    
    def test_double_quoted_string(self):
        """Test double quoted strings"""
        lexer = Lexer('"hello world"')
        tokens = lexer.tokenize()
        
        assert len(tokens) == 2  # QUOTED_STRING + EOF
        assert tokens[0].type == TokenType.QUOTED_STRING
        assert tokens[0].value == "hello world"
    
    def test_single_quoted_string(self):
        """Test single quoted strings"""
        lexer = Lexer("'hello world'")
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.QUOTED_STRING
        assert tokens[0].value == "hello world"
    
    def test_quoted_string_with_special_chars(self):
        """Test quoted strings containing special characters"""
        lexer = Lexer('"user&admin|test"')
        tokens = lexer.tokenize()
        
        assert tokens[0].value == "user&admin|test"
    
    def test_escaped_quote_in_quoted_string(self):
        """Test escaped quotes inside quoted strings"""
        lexer = Lexer(r'"she said \"hi\""')
        tokens = lexer.tokenize()
        
        assert tokens[0].value == 'she said "hi"'
    
    def test_quoted_string_with_operators(self):
        """Test quoted strings combined with operators"""
        lexer = Lexer('"first name" & "last name"')
        tokens = lexer.tokenize()
        
        assert len(tokens) == 4  # QUOTED_STRING + AND + QUOTED_STRING + EOF
        assert tokens[0].value == "first name"
        assert tokens[1].type == TokenType.AND
        assert tokens[2].value == "last name"
    
    def test_unterminated_quoted_string(self):
        """Test unterminated quoted string raises error"""
        lexer = Lexer('"unterminated')
        
        with pytest.raises(LexerError) as exc_info:
            lexer.tokenize()
        
        assert "unterminated" in str(exc_info.value).lower()
    
    def test_empty_quoted_string(self):
        """Test empty quoted string"""
        lexer = Lexer('""')
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.QUOTED_STRING
        assert tokens[0].value == ""


class TestLexerContextErrors:
    """Tests for error context reporting"""
    
    def test_error_context_simple(self):
        """Test error context is provided"""
        lexer = Lexer("abc\\")
        
        with pytest.raises(LexerError) as exc_info:
            lexer.tokenize()
        
        error = exc_info.value
        assert error.position == 4
        assert error.context is not None
        assert "^" in error.context  # Should point to error location
    
    def test_error_context_in_middle(self):
        """Test error context in middle of expression"""
        lexer = Lexer('abc "unterminated xyz')
        
        with pytest.raises(LexerError) as exc_info:
            lexer.tokenize()
        
        assert exc_info.value.context is not None