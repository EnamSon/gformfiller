# gformfiller/domain/ai/__init__.py

from typing import Type, Dict, Optional
from .base import LLMClient, LLMResponse, ModelType
from .openai_client import OpenAIClient
from .claude_client import ClaudeClient
from .gemini_client import GeminiClient
from .exceptions import AIClientException, PromptGenerationError, InvalidResponseFormatError

# Mapping of supported model types to their respective client classes
CLIENT_MAP: Dict[ModelType, Type[LLMClient]] = {
    ModelType.OPENAI: OpenAIClient,
    ModelType.CLAUDE: ClaudeClient,
    ModelType.GEMINI: GeminiClient,
}

def create_ai_client(
    model_type: ModelType, 
    api_key: str, 
    model_name: Optional[str] = None, 
    **kwargs
) -> LLMClient:
    """
    Factory function to instantiate an AI client.

    :param model_type: The provider type (ModelType.OPENAI, ModelType.CLAUDE, or ModelType.GEMINI).
    :param api_key: The API key for the chosen provider.
    :param model_name: Optional specific model name (e.g., 'gpt-4o', 'claude-3-5-sonnet-latest').
    :param kwargs: Additional arguments passed to the client constructor.
    :return: An instance of the requested LLMClient.
    :raises AIClientException: If the model type is not supported.
    """
    client_class = CLIENT_MAP.get(model_type)
    
    if not client_class:
        supported = ", ".join([m.name for m in CLIENT_MAP.keys()])
        raise AIClientException(
            f"Unsupported ModelType: {model_type}. Supported types are: {supported}"
        )

    # Prepare constructor arguments
    client_kwargs = {"api_key": api_key}
    if model_name:
        client_kwargs["model_name"] = model_name
    
    # Merge with additional kwargs
    client_kwargs.update(kwargs)

    return client_class(**client_kwargs)

__all__ = [
    'create_ai_client',
    'LLMClient',
    'LLMResponse',
    'ModelType',
    'OpenAIClient',
    'ClaudeClient',
    'GeminiClient',
    'AIClientException',
    'PromptGenerationError',
    'InvalidResponseFormatError'
]