# gformfiller/domain/schemas/metadata.py

from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional

class FillerMetadata(BaseModel):
    url: HttpUrl = Field(..., description="L'URL complète du Google Form")
    created_at: datetime = Field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    status: str = "initialized" # ready, running, completed, error
    description: Optional[str] = None