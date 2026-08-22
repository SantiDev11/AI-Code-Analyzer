"""Excepciones de dominio para el modulo de Inteligencia Artificial.

Ninguna excepcion expone claves secretas ni tokens en sus mensajes.
"""


class AIError(Exception):
    """Error generico del modulo de Inteligencia Artificial."""


class AIConfigurationError(AIError):
    """Error de configuracion de IA (falta de API key o proveedor invalido)."""


class AIProviderError(AIError):
    """Error de comunicacion o respuesta no exitosa del proveedor de IA."""


class AIRateLimitError(AIProviderError):
    """Cuota agotada o limite de tasa de peticiones alcanzado en el proveedor de IA."""


class AIResponseValidationError(AIError):
    """La respuesta del proveedor de IA no cumple el contrato o formato Pydantic esperado."""
