# gformfiller/domain/ai/gemini_client.py

import logging
from google import genai
from typing import List, Dict, Any
from .base import LLMClient, LLMResponse, AIClientException 

logger = logging.getLogger(__name__)

class GeminiClient(LLMClient):
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash", **kwargs):
        super().__init__(api_key=api_key, model_name=model_name, **kwargs)
        self._client = genai.Client(api_key=api_key)

    def generate_page_answers(
        self, 
        questions_data: List[Dict[str, Any]], 
        user_prompt: str
    ) -> LLMResponse:
        
        system_prompt = self._create_page_system_prompt(questions_data)
        
        try:
            logger.info(f"Gemini: Processing {len(questions_data)} questions.")
            
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=[user_prompt],
                config={
                    "system_instruction": system_prompt,
                    "temperature": 0.0
                }
            )
            
            # Gemini response.text can raise an error or be empty if blocked
            raw_text = response.text
            
            if not raw_text:
                logger.error("Gemini returned an empty response. It might be blocked by safety filters.")
                raise AIClientException("Gemini returned no content.")

            return LLMResponse(raw_output=raw_text.strip(), expected_count=len(questions_data))

        except Exception as e:
            logger.error(f"Gemini Error: {e}")
            raise AIClientException(f"Gemini call failed: {e}")