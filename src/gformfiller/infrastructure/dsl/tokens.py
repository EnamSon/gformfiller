# infrastructure/dsl/tokens.py

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any


class TokenType(Enum):
    """Token types for DSL"""
    
    # Literals
    WORD = auto()              # Simple word: abc
    ESCAPED_WORD = auto()      # Word with escaped characters: abc\&def
    QUOTED_STRING = auto()     # String between quotation marks: "abc def"
    
    # Operators
    AND = auto()               # &
    OR = auto()                # |
    NOT = auto()               # ~
    BEFORE = auto()            # <
    
    # Grouping
    LPAREN = auto()            # (
    RPAREN = auto()            # )
    
    # Special
    EOF = auto()               # End of input
    WHITESPACE = auto()        # Espace (ignored except in escape)


@dataclass
class Token:
    """Token with position information"""
    type: TokenType
    value: Any
    position: int              # Position in the original string
    length: int                # Length of the token
    
    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, pos={self.position})"