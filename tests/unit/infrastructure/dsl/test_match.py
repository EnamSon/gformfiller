# tests/unit/infrastructure/dsl/test_match.py

import pytest
import logging
from typing import List, Tuple, Any

import gformfiller.infrastructure.dsl as dsl
from gformfiller.infrastructure.dsl.examples import EXAMPLES

# Fixture to flatten the EXAMPLES dictionary for easy pytest parameterization
def get_match_params():
    """Prepares parameters for success and failure tests."""
    params = []
    for test_name, data in EXAMPLES.items():
        expr = data['expression']
        
        # Success cases (match must be True)
        for text in data.get('matches', []):
            # Using a short snippet of the text for a readable test ID
            text_id = text[:20].replace(' ', '_').replace('"', '')
            params.append(pytest.param(expr, text, True, id=f"MATCH-{test_name}-{text_id}"))
            
        # Failure cases (match must be False)
        for text in data.get('no_matches', []):
            text_id = text[:20].replace(' ', '_').replace('"', '')
            params.append(pytest.param(expr, text, False, id=f"NO_MATCH-{test_name}-{text_id}"))
    return params

# Fixture for syntax error cases
def get_error_params():
    """Prepares expressions that are expected to cause a syntax error (Lexer or Parser)."""
    return [
        pytest.param("A & (B", id="PARSER-Unbalanced-Parens"),
        pytest.param("A &", id="PARSER-Missing-Operand"),
        pytest.param('"unclosed', id="LEXER-Unclosed-Quote"),
        pytest.param('A < "B', id="LEXER-Unclosed-Quote-2"),
    ]


@pytest.mark.parametrize("expression, text, expected_result", get_match_params())
def test_match_success_and_failure_cases(expression: str, text: str, expected_result: bool):
    """Tests standard success and failure evaluation cases using the default ignore_case=True."""
    result = dsl.match(text, expression)
    assert result is expected_result


def test_match_ignore_case_true():
    """Tests case-insensitivity (default behavior). Both inputs are lowercased by match()."""
    expression = "PyThOn & ~JaVa"
    text_match = "I use PYTHON for everything"
    text_no_match = "I use JAVASCRIPT for everything"
    
    # Should work because 'match' normalizes both inputs
    assert dsl.match(text_match, expression, ignore_case=True) is True
    assert dsl.match(text_no_match, expression, ignore_case=True) is False


def test_match_ignore_case_false():
    """Tests case-sensitivity (where text must match term case exactly)."""
    expression = "USER"
    text_match = "I found the USER account"
    text_no_match = "I found the user account"
    
    # Case sensitive test
    assert dsl.match(text_match, expression, ignore_case=False) is True
    assert dsl.match(text_no_match, expression, ignore_case=False) is False
    
    # Test with lowercase expression
    expression_lower = "user"
    assert dsl.match("I found the user account", expression_lower, ignore_case=False) is True
    assert dsl.match("I found the USER account", expression_lower, ignore_case=False) is False


@pytest.mark.parametrize("expression", get_error_params())
def test_match_syntax_errors_return_none_and_log(expression: str, caplog):
    """Tests that syntax errors (Lexer or Parser) return None and log the error."""
    
    # Capture the log to verify the error record
    with caplog.at_level(logging.ERROR, logger='infrastructure.dsl'):
        result = dsl.match("some text", expression)
        
    # Verify the result is None
    assert result is None
    
    # Verify that the error was logged
    assert len(caplog.records) >= 1
    assert "DSL expression failed evaluation or parsing." in caplog.text


def test_match_empty_inputs():
    """Tests edge cases with empty strings."""
    
    # Empty expression, should return True (handled by the guard in match)
    assert dsl.match("some text", "") is True
    
    # Empty text, non-empty expression, should return False
    assert dsl.match("", "A & B") is False
    
    # Empty expression and text, should return True
    assert dsl.match("", "") is True