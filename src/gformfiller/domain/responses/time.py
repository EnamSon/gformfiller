# gformfiller/domain/responses/time.py

from gformfiller.infrastructure.element_locators import (
    GoogleFormElement, ElementNotFoundError
)
from .base import BaseResponse
from .constants import ResponseType
from .exceptions import ElementTypeMismatchError, InvalidResponseExpressionError
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class TimeResponse(BaseResponse):
    """Handler for time input fields (separate hour and minute inputs)."""

    def set_type(self) -> ResponseType:
        """
        Sets the type to TIME and validates the presence of the hour and minute input elements.
        
        :raises ElementTypeMismatchError: If the hour or minute input is not found within the question container.
        """
        try:
            self._hour_element = self.locator.locate(GoogleFormElement.TIME_HOUR)
            self._minute_element = self.locator.locate(GoogleFormElement.TIME_MINUTE)
        except ElementNotFoundError as e:
            raise ElementTypeMismatchError(ResponseType.TIME.name, self._element.tag_name) from e
        return ResponseType.TIME

    def _parse_time_expression(self, dsl_expression: str) -> Tuple[str, str]:
        """
        Parses the DSL expression (e.g., "14:30") and validates the hour and minute components.

        :param dsl_expression: The time string (HH:MM format).
        :return: A tuple (hour_string, minute_string).
        :raises InvalidResponseExpressionError: If the expression format or values are invalid.
        """
        parts = dsl_expression.split(':')
        
        if len(parts) != 2:
            raise InvalidResponseExpressionError(
                self.response_type.name,
                dsl_expression,
                "Expected a valid time format string (e.g., HH:MM)."
            )

        try:
            hour = int(parts[0])
            minute = int(parts[1])
            
            # Validation des plages horaires (0-23 pour heure, 0-59 pour minute)
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                 raise ValueError("Time values out of range (HH: 00-23, MM: 00-59).")
            
            # Retourne les valeurs formatées en chaîne (ex: '09', '05') pour send_keys
            return f"{hour:02d}", f"{minute:02d}"
            
        except ValueError as e:
            raise InvalidResponseExpressionError(
                self.response_type.name,
                dsl_expression,
                f"Hour and minute must be valid integers. Error: {e}"
            )

    def push(self, dsl_expression: str) -> bool:
        """
        Pushes the time represented by the DSL expression into the hour and minute input fields.

        :param dsl_expression: The time string (HH:MM format).
        :return: True if successful.
        """
        try:
            # 1. Analyser et valider l'expression
            hour_str, minute_str = self._parse_time_expression(dsl_expression)
            
            # 2. Application des actions
            
            # Pour éviter les problèmes si l'input a déjà une valeur, on clear d'abord
            self._hour_element.clear()
            self._hour_element.send_keys(hour_str)
            
            self._minute_element.clear()
            self._minute_element.send_keys(minute_str)
            
            logger.info(
                f"Successfully set Time field to '{hour_str}:{minute_str}'."
            )
            return True
            
        except InvalidResponseExpressionError:
            # Relever l'erreur sans logger la stack trace, car c'est une erreur de données utilisateur
            raise
        except Exception as e:
            logger.error(
                f"Failed to push time '{dsl_expression}' to element: {e}", 
                exc_info=True
            )
            # Wrapper l'exception pour le domaine si nécessaire, sinon la relever
            raise