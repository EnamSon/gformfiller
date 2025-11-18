# infrastructure/dsl/parser.py

from typing import List, Optional
from .tokens import Token, TokenType
from .ast_nodes import (
    ASTNode, WordNode, QuotedStringNode,
    AndNode, OrNode, NotNode, BeforeNode
)
from .exceptions import ParserError


class Parser:
    """
    Recursive Descent Parser for the DSL.
    
    Grammar Hierarchy (Precedence from low to high):
    1. Expression (OR)
    2. AndTerm (AND)
    3. BeforeTerm (BEFORE)
    4. Factor (NOT, parens, literals)
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        if not tokens:
            raise ValueError("Empty tokens list.")
        self.current_token = self.tokens[0]

    def error(self, message: str) -> ParserError:
        return ParserError(message, self.current_token)

    def eat(self, token_type: TokenType) -> None:
        """
        Consume the current token if it matches the expected type.
        Otherwise, raise an error.
        """
        if self.current_token.type == token_type:
            self.advance()
        else:
            raise self.error(
                f"Unexpected token. Expected {token_type.name}, got {self.current_token.type.name}"
            )

    def advance(self) -> None:
        """Move to the next token."""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = Token(TokenType.EOF, None, -1, 0)

    def parse(self) -> ASTNode:
        """Public entry point."""
        if not self.tokens or self.current_token.type == TokenType.EOF:
            raise self.error("Empty input")
            
        node = self.expression()
        
        if self.current_token.type != TokenType.EOF:
            raise self.error("Unexpected content after expression end")
            
        return node

    # --- Grammar Rules ---

    def expression(self) -> ASTNode:
        """
        expression : and_term (OR and_term)*
        """
        node = self.and_term()

        while self.current_token.type == TokenType.OR:
            self.eat(TokenType.OR)
            node = OrNode(left=node, right=self.and_term())

        return node

    def and_term(self) -> ASTNode:
        """
        and_term : before_term (AND before_term)*
        """
        node = self.before_term()

        while self.current_token.type == TokenType.AND:
            self.eat(TokenType.AND)
            node = AndNode(left=node, right=self.before_term())

        return node

    def before_term(self) -> ASTNode:
        """
        before_term : factor (BEFORE factor)*
        """
        node = self.factor()

        while self.current_token.type == TokenType.BEFORE:
            self.eat(TokenType.BEFORE)
            node = BeforeNode(left=node, right=self.factor())

        return node

    def factor(self) -> ASTNode:
        """
        factor : NOT factor
               | LPAREN expression RPAREN
               | atom
        """
        token = self.current_token

        if token.type == TokenType.NOT:
            self.eat(TokenType.NOT)
            return NotNode(operand=self.factor())

        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expression()
            self.eat(TokenType.RPAREN)
            return node

        else:
            return self.atom()

    def atom(self) -> ASTNode:
        """
        atom : WORD | QUOTED_STRING
        """
        token = self.current_token

        if token.type == TokenType.WORD:
            self.eat(TokenType.WORD)
            return WordNode(value=token.value)
        
        elif token.type == TokenType.ESCAPED_WORD:
            self.eat(TokenType.ESCAPED_WORD)
            return WordNode(value=token.value)

        elif token.type == TokenType.QUOTED_STRING:
            self.eat(TokenType.QUOTED_STRING)
            return QuotedStringNode(value=token.value)

        else:
            raise self.error(f"Unexpected token in atom: {token.type}")