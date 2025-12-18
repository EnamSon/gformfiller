# gformfiller/domain/ai/claude_client.py

import logging
import anthropic
from typing import List, Dict, Any
from .base import LLMClient, LLMResponse, AIClientException 

logger = logging.getLogger(__name__)

class ClaudeClient(LLMClient):
    def __init__(self, api_key: str, model_name: str = "claude-3-5-sonnet", **kwargs):
        super().__init__(api_key=api_key, model_name=model_name, **kwargs)
        self._client = anthropic.Anthropic(api_key=api_key)

    def generate_page_answers(
        self, 
        questions_data: List[Dict[str, Any]], 
        user_prompt: str
    ) -> LLMResponse:
        
        system_prompt = self._create_page_system_prompt(questions_data)
        user_message = f"USER CONTEXT:\n{user_prompt}"

        try:
            logger.info(f"Claude: Processing {len(questions_data)} questions.")
            
            response = self._client.messages.create(
                model=self.model_name,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                max_tokens=4096,
                temperature=0.0
            )
            
            # Handling potential None or empty content list
            if not response.content or response.content[0].type != "text":
                logger.error(f"Claude returned unexpected content type or empty response.")
                raise AIClientException("Claude returned no text content.")

            raw_text = response.content[0].text
            return LLMResponse(raw_output=raw_text.strip(), expected_count=len(questions_data))

        except anthropic.AnthropicError as e:
            logger.error(f"Claude API Error: {e}")
            raise AIClientException(f"Claude communication failed: {e}")
        except Exception as e:
            logger.error(f"Claude Unexpected Error: {e}")
            raise AIClientException(f"Failed to fetch batch answers: {e}")