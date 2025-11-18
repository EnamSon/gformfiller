import pytest
from gformfiller.infrastructure.dsl.evaluator import Evaluator
from gformfiller.infrastructure.dsl.ast_nodes import (
    WordNode, QuotedStringNode, AndNode, OrNode, NotNode, BeforeNode
)

@pytest.fixture
def evaluator():
    return Evaluator()

def test_literal_match(evaluator):
    node = WordNode("python")
    assert evaluator.evaluate(node, "I love python programming") is True
    assert evaluator.evaluate(node, "I love java") is False

def test_case_insensitivity(evaluator):
    node = WordNode("Python")
    # Should match "python", "PYTHON", "PyThOn"
    assert evaluator.evaluate(node, "coding in python") is True
    assert evaluator.evaluate(node, "CODING IN PYTHON") is True

def test_quoted_string(evaluator):
    node = QuotedStringNode("data science")
    assert evaluator.evaluate(node, "Expert in data science") is True
    assert evaluator.evaluate(node, "Expert in data and science") is False

def test_and_logic(evaluator):
    # A & B
    node = AndNode(WordNode("fast"), WordNode("furious"))
    assert evaluator.evaluate(node, "fast and furious") is True
    assert evaluator.evaluate(node, "fast but slow") is False
    assert evaluator.evaluate(node, "calm and furious") is False

def test_or_logic(evaluator):
    # A | B
    node = OrNode(WordNode("cat"), WordNode("dog"))
    assert evaluator.evaluate(node, "I have a cat") is True
    assert evaluator.evaluate(node, "I have a dog") is True
    assert evaluator.evaluate(node, "I have a hamster") is False

def test_not_logic(evaluator):
    # ~java
    node = NotNode(WordNode("java"))
    assert evaluator.evaluate(node, "python code") is True
    assert evaluator.evaluate(node, "java code") is False

def test_before_operator_basic(evaluator):
    # first < last
    node = BeforeNode(WordNode("first"), WordNode("last"))
    
    assert evaluator.evaluate(node, "first name then last name") is True
    assert evaluator.evaluate(node, "last name then first name") is False
    assert evaluator.evaluate(node, "only first name") is False

def test_before_operator_strict_sequence(evaluator):
    # a < b
    node = BeforeNode(WordNode("a"), WordNode("b"))
    
    # "b a b" -> le premier "a" est à l'index 2. Un "b" existe après (index 4).
    # Cela devrait être Vrai.
    assert evaluator.evaluate(node, "b a b") is True
    
    # "b a" -> "a" est là, mais pas de "b" après lui.
    assert evaluator.evaluate(node, "b a") is False

def test_nested_before(evaluator):
    # (a < b) < c
    # Note: Le parser grouperait probablement ainsi pour "a < b < c"
    node = BeforeNode(
        BeforeNode(WordNode("a"), WordNode("b")),
        WordNode("c")
    )
    
    assert evaluator.evaluate(node, "a then b then c") is True
    assert evaluator.evaluate(node, "a then c then b") is False

@pytest.mark.parametrize("text,expected", [
    ("start the process and end it", True),
    ("begin the process and end it", True),
    ("end the process before you start", False),
    ("completely irrelevant text", False),
])
def test_complex_before_with_or(evaluator, text, expected):
    """
    Expression: (start | begin) < end
    """
    node = BeforeNode(
        OrNode(WordNode("start"), WordNode("begin")),
        WordNode("end")
    )
    assert evaluator.evaluate(node, text) is expected

def test_empty_text(evaluator):
    node = WordNode("something")
    assert evaluator.evaluate(node, "") is False
    assert evaluator.evaluate(node, None) is False