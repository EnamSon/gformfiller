# gformfiller/domain/ai/base.py

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from enum import Enum
import logging
from .exceptions import AIClientException

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Enumeration of supported LLM providers."""
    OPENAI = "openai"
    GEMINI = "gemini"
    CLAUDE = "claude"
    COPILOT = "copilot"
    DEEPSEEK = "deepseek"

class LLMResponse:
    """
    Holds the processed answers as a list where index i matches question i.
    """
    def __init__(self, raw_output: str, expected_count: int | None = None):
        self.raw_output = raw_output
        # Split by double newline to match the questions_data indexing
        self.answers: List[str] = [ans.strip() for ans in raw_output.split("\n\n")]
        if isinstance(expected_count, int) and len(self.answers) != expected_count:
            logger.warning(f"Mismatch: Expected {expected_count} answers, but LLM returned {len(self.answers)}.")

class LLMClient(ABC):
    def __init__(self, api_key: str, model_name: str, **kwargs):
        self._api_key = api_key
        self.model_name = model_name

    @abstractmethod
    def generate_page_answers(
        self, 
        questions_data: List[Dict[str, Any]], 
        user_prompt: str
    ) -> LLMResponse:
        """
        Sends questions to LLM and returns an LLMResponse containing 
        the ordered list of answers.
        """
        pass

    def _create_page_system_prompt(self, questions_data: List[Dict[str, Any]]) -> str:
        from .constants import SYSTEM_INSTRUCTION_BASE, DSL_RULES
        
        prompt = [SYSTEM_INSTRUCTION_BASE, DSL_RULES, "\nQUESTIONS TO ANSWER (STRICT ORDER):"]
        for i, q in enumerate(questions_data, 1):
            q_info = f"{i}. Question: '{q['text']}' (Type: {q['type']})"
            if q.get('options'):
                q_info += f" | Options: {q['options']}"
            prompt.append(q_info)
            
        return "\n".join(prompt)