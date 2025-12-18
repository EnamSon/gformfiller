# gformfiller/domain/schemas/config.py

from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class AIModelProvider(str, Enum):
    OPENAI = "OPENAI"
    ANTHROPIC = "ANTHROPIC"
    GEMINI = "GEMINI"

class FillerConfig(BaseModel):
    # Browser settings
    profile: str = Field(default="default", description="Nom du dossier dans profiles/")
    headless: bool = False
    wait_time: float = Field(default=10.0, ge=0.5) # Minimum 0.5s
    remote: bool = False
    max_retries: int = Field(default=2, ge=0, le=5)

    # AI settings
    use_ai: bool = False
    model_type: AIModelProvider = AIModelProvider.OPENAI
    model_name: str = "gpt-4o"
    
    # Automation settings
    submit: bool = False