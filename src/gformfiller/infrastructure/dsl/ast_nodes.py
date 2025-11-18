# infrastructure/dsl/ast_nodes.py

from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any


class ASTNode(ABC):
    """
    Abstract base class for all AST nodes.
    """
    @abstractmethod
    def __repr__(self) -> str:
        pass


# --- Literal Nodes ---

@dataclass
class LiteralNode(ASTNode):
    """Base class for text literals."""
    value: str

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"


@dataclass
class WordNode(LiteralNode):
    r"""Represents a single word or escaped sequence (e.g., user\&admin)."""
    pass


@dataclass
class QuotedStringNode(LiteralNode):
    """Represents a phrase enclosed in quotes (e.g., "hello world")."""
    pass


# --- Operator Nodes ---

@dataclass
class UnaryOpNode(ASTNode):
    """Base class for unary operators like NOT."""
    operand: ASTNode

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.operand})"


@dataclass
class NotNode(UnaryOpNode):
    """Represents the negation operator (~)."""
    pass


@dataclass
class BinaryOpNode(ASTNode):
    """Base class for binary operators (AND, OR, BEFORE)."""
    left: ASTNode
    right: ASTNode

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(left={self.left}, right={self.right})"


@dataclass
class AndNode(BinaryOpNode):
    """Represents the logical AND (&)."""
    pass


@dataclass
class OrNode(BinaryOpNode):
    """Represents the logical OR (|)."""
    pass


@dataclass
class BeforeNode(BinaryOpNode):
    """Represents the sequencing operator (<)."""
    pass