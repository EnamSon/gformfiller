import pytest
from gformfiller.infrastructure.dsl.tokens import Token, TokenType
from gformfiller.infrastructure.dsl.parser import Parser
from gformfiller.infrastructure.dsl.exceptions import ParserError
from gformfiller.infrastructure.dsl.ast_nodes import (
    WordNode, QuotedStringNode, AndNode, OrNode, NotNode, BeforeNode
)

@pytest.fixture
def parse_helper():
    """
    Helper fixture to simplify token creation and parsing.
    Accepts a list of (TokenType, value) tuples.
    """
    def _parse(token_data):
        tokens = []
        pos = 0
        for t_type, t_val in token_data:
            # Calculate length simply for the mock
            length = len(t_val) if t_val else 1
            tokens.append(Token(t_type, t_val, pos, length))
            pos += length
        
        # Add EOF
        tokens.append(Token(TokenType.EOF, None, pos, 0))
        
        parser = Parser(tokens)
        return parser.parse()
    return _parse

def test_parse_simple_word(parse_helper):
    ast = parse_helper([(TokenType.WORD, "test")])
    assert isinstance(ast, WordNode)
    assert ast.value == "test"

def test_parse_quoted_string(parse_helper):
    ast = parse_helper([(TokenType.QUOTED_STRING, "hello world")])
    assert isinstance(ast, QuotedStringNode)
    assert ast.value == "hello world"

def test_operator_precedence_and_or(parse_helper):
    """
    Test logic: A | B & C should be parsed as A | (B & C) 
    because AND has higher precedence than OR.
    """
    # A | B & C
    ast = parse_helper([
        (TokenType.WORD, "A"),
        (TokenType.OR, "|"),
        (TokenType.WORD, "B"),
        (TokenType.AND, "&"),
        (TokenType.WORD, "C"),
    ])
    
    # Root should be OR
    assert isinstance(ast, OrNode)
    assert ast.left.value == "A"
    
    # Right side should be AND
    assert isinstance(ast.right, AndNode)
    assert ast.right.left.value == "B"
    assert ast.right.right.value == "C"

def test_operator_precedence_before_and(parse_helper):
    """
    Test logic: A & B < C should be A & (B < C)
    """
    ast = parse_helper([
        (TokenType.WORD, "A"),
        (TokenType.AND, "&"),
        (TokenType.WORD, "B"),
        (TokenType.BEFORE, "<"),
        (TokenType.WORD, "C"),
    ])
    
    assert isinstance(ast, AndNode)
    assert isinstance(ast.right, BeforeNode)
    assert ast.right.left.value == "B"
    assert ast.right.right.value == "C"

def test_parentheses_override(parse_helper):
    """
    Test logic: (A | B) & C
    """
    ast = parse_helper([
        (TokenType.LPAREN, "("),
        (TokenType.WORD, "A"),
        (TokenType.OR, "|"),
        (TokenType.WORD, "B"),
        (TokenType.RPAREN, ")"),
        (TokenType.AND, "&"),
        (TokenType.WORD, "C"),
    ])
    
    assert isinstance(ast, AndNode)
    assert isinstance(ast.left, OrNode)
    assert ast.left.left.value == "A"
    assert ast.left.right.value == "B"
    assert ast.right.value == "C"

def test_not_operator(parse_helper):
    """Test logic: ~A"""
    ast = parse_helper([
        (TokenType.NOT, "~"),
        (TokenType.WORD, "A"),
    ])
    
    assert isinstance(ast, NotNode)
    assert isinstance(ast.operand, WordNode)
    assert ast.operand.value == "A"

def test_error_missing_operand(parse_helper):
    """Test error: A & (EOF)"""
    with pytest.raises(ParserError) as excinfo:
        parse_helper([
            (TokenType.WORD, "A"),
            (TokenType.AND, "&"),
        ])

    error_message = str(excinfo.value).lower()
    assert error_message.startswith("unexpected")

def test_error_unbalanced_parens(parse_helper):
    """Test error: (A | B"""
    with pytest.raises(ParserError):
        parse_helper([
            (TokenType.LPAREN, "("),
            (TokenType.WORD, "A"),
            (TokenType.OR, "|"),
            (TokenType.WORD, "B"),
        ])