# gformfiller/domain/schemas/form_data.py

from pydantic import BaseModel, RootModel
from typing import Dict

# Rappel de la structure : 
# { "TextResponse": { "Nom": "John" }, "CheckboxResponse": { "Hobbies": "Sport|Musique" } }
class FormDataSchema(RootModel):
    root: Dict[str, Dict[str, str]]

    def get_answers_for_type(self, response_type: str) -> Dict[str, str]:
        return self.root.get(response_type, {})