"""Cliente HTTP desacoplado para comunicarse con proveedores de IA compatibles con OpenAI."""

import json
from typing import Any

import httpx

from app.config import settings
from app.services.ai.exceptions import (
    AIConfigurationError,
    AIProviderError,
    AIRateLimitError,
    AIResponseValidationError,
)


def _build_endpoint_url(base_url: str) -> str:
    """Construye la URL del endpoint /chat/completions evitando duplicaciones."""
    url = base_url.strip().rstrip("/")
    if url.endswith("/chat/completions"):
        return url
    if url.endswith("/v1"):
        return f"{url}/chat/completions"
    return f"{url}/v1/chat/completions"


def _build_headers(api_key: str | None) -> dict[str, str]:
    """Construye las cabeceras HTTP sin exponer secretos."""
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _create_ai_client() -> httpx.AsyncClient:
    """Crea el cliente HTTP para comunicarse con el proveedor de IA.

    Punto de sustitucion para los tests unitarios.
    """
    return httpx.AsyncClient(timeout=httpx.Timeout(settings.ai_timeout_seconds))


async def complete_chat(
    system_prompt: str,
    user_payload: dict[str, Any],
    *,
    api_key: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
) -> str:
    """Envia una solicitud de chat completion y devuelve el contenido del mensaje."""
    key = api_key if api_key is not None else settings.ai_api_key
    selected_model = model or settings.ai_model
    selected_base_url = base_url or settings.ai_base_url

    endpoint = _build_endpoint_url(selected_base_url)
    headers = _build_headers(key)

    body = {
        "model": selected_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
    }

    async with _create_ai_client() as client:
        try:
            response = await client.post(endpoint, headers=headers, json=body)
        except httpx.TimeoutException as error:
            raise AIProviderError("Tiempo de espera agotado al consultar la IA") from error
        except httpx.RequestError as error:
            raise AIProviderError("Fallo de conexion con el proveedor de IA") from error

    if response.status_code in (401, 403):
        raise AIConfigurationError(
            f"Error de autenticacion con el proveedor de IA (codigo {response.status_code})"
        )

    if response.status_code in (429,):
        raise AIRateLimitError("Cuota agotada o limite de tasa alcanzado en el proveedor de IA")

    if not response.is_success:
        raise AIProviderError(f"El proveedor de IA respondio con error HTTP {response.status_code}")

    try:
        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            raise AIResponseValidationError("El proveedor de IA devolvio una lista de choices vacia")
        message = choices[0].get("message", {})
        content = message.get("content")
        if not content:
            raise AIResponseValidationError("El mensaje devuelto por la IA no contiene content")
        return str(content)
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as error:
        raise AIResponseValidationError(
            f"Estructura de respuesta HTTP invalida del proveedor de IA: {error}"
        ) from error
