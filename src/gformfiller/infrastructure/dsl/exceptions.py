# infrastructure/dsl/exceptions.py

class DSLError(Exception):
    """Base exception for DSL errors"""
    pass


class LexerError(DSLError):
    """Raised when lexer encounters invalid syntax"""
    
    def __init__(self, message: str, position: int, context: str):
        self.message = message
        self.position = position
        self.context = context
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        return f"{self.message} at position {self.position}\n{self.context}"


class ParserError(DSLError):
    """Raised when parser encounters invalid syntax"""
    
    def __init__(self, message: str, token=None):
        self.message = message
        self.token = token
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        if self.token:
            return f"{self.message} at position {self.token.position} (token: {self.token})"
        return self.message


class EvaluationError(DSLError):
    """Raised when evaluation fails"""
    pass