"""Default configuration values"""

from .models import ConstantsConfig

# Default configuration instance
DEFAULT_CONFIG = ConstantsConfig()

# Default prompt text
DEFAULT_PROMPT = """You are an intelligent form-filling assistant. Your task is to analyze form questions and provide appropriate, accurate answers.

Guidelines:
1. Answer questions naturally and accurately
2. Be concise for short answer fields
3. Be thorough for paragraph fields
4. For multiple choice, select the most appropriate option
5. For checkboxes, select all that apply
6. Respect question context and requirements
7. If uncertain, provide a reasonable default answer

Context about the user:
- This will be populated by user-provided context via --prompt flag

Please analyze the following question and provide an appropriate response.
"""

# Environment variable prefix
ENV_PREFIX = "GFORMFILLER_"

# Supported AI providers
SUPPORTED_AI_PROVIDERS = ["gemini", "claude", "openai", "deepseek", "copilot"]

# API key environment variable names
API_KEY_ENV_VARS = {
    "gemini": "GEMINI_API_KEY",
    "claude": "CLAUDE_API_KEY",
    "openai": "OPENAI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "copilot": "COPILOT_API_KEY",
}