# infrastructure/dsl/evaluator.py

from .ast_nodes import (
    ASTNode, WordNode, QuotedStringNode, 
    AndNode, OrNode, NotNode, BeforeNode
)
from .exceptions import EvaluationError


class Evaluator:
    """
    Evaluates an AST against a target text string using boolean logic
    and positional awareness.
    """

    def evaluate(self, node: ASTNode, text: str) -> bool:
        """
        Evaluate if the AST conditions are met within the text.
        """
        if not text:
            return False
        return self._visit(node, text)

    def _visit(self, node: ASTNode, text: str) -> bool:
        """Dispatch based on node type."""
        
        # Literals
        if isinstance(node, (WordNode, QuotedStringNode)):
            return node.value in text
            
        # Binary Ops
        elif isinstance(node, AndNode):
            return self._visit(node.left, text) and self._visit(node.right, text)
            
        elif isinstance(node, OrNode):
            return self._visit(node.left, text) or self._visit(node.right, text)
        
        # Unary Ops
        elif isinstance(node, NotNode):
            return not self._visit(node.operand, text)
            
        # Positional Ops
        elif isinstance(node, BeforeNode):
            return self._visit_before(node, text)
            
        else:
            raise EvaluationError(f"Unknown node type: {type(node).__name__}")

    def _visit_before(self, node: BeforeNode, text: str) -> bool:
        """
        Validates 'Left < Right'.
        Finds the first occurrence of Left, then searches for Right *after* that index.
        """
        # Find the start position of the left operand
        left_index = self._find_index(node.left, text, start=0)
        
        if left_index == -1:
            return False # Left side not found, so condition fails
            
        # We search for the right operand starting strictly after the left one starts.
        # (Note: strictly speaking, we should start after left ends, but since we don't 
        # store token length in AST easily, 'start + 1' ensures strict ordering of starts)
        right_index = self._find_index(node.right, text, start=left_index + 1)
        
        return right_index != -1

    def _find_index(self, node: ASTNode, text: str, start: int) -> int:
        """
        Helper to find the *earliest* valid index of a node match 
        starting from 'start'. Returns -1 if not found.
        """
        if start >= len(text):
            return -1

        if isinstance(node, (WordNode, QuotedStringNode)):
            return text.find(node.value, start)

        elif isinstance(node, OrNode):
            # Find the earliest match of either branch
            idx_left = self._find_index(node.left, text, start)
            idx_right = self._find_index(node.right, text, start)
            
            if idx_left == -1: return idx_right
            if idx_right == -1: return idx_left
            return min(idx_left, idx_right)

        elif isinstance(node, AndNode):
            idx_left = self._find_index(node.left, text, start)
            idx_right = self._find_index(node.right, text, start)
            
            if idx_left != -1 and idx_right != -1:
                return min(idx_left, idx_right)
            return -1

        elif isinstance(node, BeforeNode):
            # Recursively verify the sequence exists starting from 'start'
            idx_left = self._find_index(node.left, text, start)
            if idx_left == -1: return -1
            
            # If left matches, check right
            idx_right = self._find_index(node.right, text, idx_left + 1)
            if idx_right != -1:
                return idx_right 
            return -1

        elif isinstance(node, NotNode):
            return -1

        return -1