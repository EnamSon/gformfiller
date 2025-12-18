import logging
from typing import Optional
from .lexer import Lexer
from .parser import Parser
from .evaluator import Evaluator
from .exceptions import DSLError, LexerError, ParserError, EvaluationError

logger = logging.getLogger(__name__)


def match(text: str, expression: str, ignore_case: bool = True) -> Optional[bool]:
    """
    Evaluates if a given text matches a DSL expression.

    This function orchestrates the complete DSL chain:
    1. Pre-processing (Case normalization)
    2. Lexing (Tokenization)
    3. Parsing (AST Construction)
    4. Evaluation of the AST against the text

    Args:
        text (str): The target text to search within.
        expression (str): The search expression in DSL format.
        ignore_case (bool): If True, both text and expression are lowercased
                            before processing. Defaults to True.

    Returns:
        Optional[bool]: True if the text matches, False otherwise.
                        Returns None if a DSL syntax error or evaluation error
                        occurs.
    """
    if not expression:
        return True
        
    try:
        # 1. Pre-processing: Case normalization
        if ignore_case:
            text = text.lower()
            expression = expression.lower()

        # 2. Lexing: Convert the expression into a list of tokens
        lexer = Lexer(expression)
        tokens = lexer.tokenize()

        # 3. Parsing: Convert the token list into an AST
        parser = Parser(tokens)
        ast = parser.parse()

        # 4. Evaluation: Evaluate the AST against the target text
        evaluator = Evaluator()
        result = evaluator.evaluate(ast, text)

        return result

    except (LexerError, ParserError, EvaluationError) as e:
        # Log the specific DSL error before returning None
        logger.error(
            "DSL expression failed evaluation or parsing.",
            exc_info=True,
            extra={
                'expression': expression, 
                'text_snippet': text[:50] + '...' if len(text) > 50 else text
            }
        )
        return None