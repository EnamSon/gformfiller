# gformfiller/domain/ai/openai_client.py

import logging
import openai
from typing import List, Dict, Any
from .base import LLMClient, LLMResponse, AIClientException 

logger = logging.getLogger(__name__)

class OpenAIClient(LLMClient):
    def __init__(self, api_key: str, model_name: str = "gpt-4-turbo", **kwargs):
        super().__init__(api_key=api_key, model_name=model_name, **kwargs)
        self._client = openai.OpenAI(api_key=api_key)

    def generate_page_answers(
        self, 
        questions_data: List[Dict[str, Any]], 
        user_prompt: str
    ) -> LLMResponse:
        
        system_prompt = self._create_page_system_prompt(questions_data)
        user_message = f"USER CONTEXT / PERSONAL DATA:\n{user_prompt}"

        try:
            logger.info(f"OpenAI: Generating answers for {len(questions_data)} questions.")
            
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.0
            )
            
            # --- Safety Check for None content ---
            raw_text = response.choices[0].message.content
            
            if raw_text is None:
                # This happens if the model returns a null response (e.g., content filter)
                finish_reason = response.choices[0].finish_reason
                logger.error(f"OpenAI returned an empty response. Finish reason: {finish_reason}")
                raise AIClientException(f"AI returned no content (Finish reason: {finish_reason})")

            return LLMResponse(
                raw_output=raw_text.strip(),
                expected_count=len(questions_data)
            )

        except openai.OpenAIError as e:
            logger.error(f"OpenAI API Error: {e}")
            raise AIClientException(f"OpenAI API communication failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI client: {e}")
            raise AIClientException(f"Failed to fetch batch answers: {e}")