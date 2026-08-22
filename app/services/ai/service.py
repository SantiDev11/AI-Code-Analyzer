"""Servicio principal de analisis con Inteligencia Artificial.

Orquesta la generacion de prompts, la construccion de contexto y la validacion
estricta Pydantic de la respuesta.
"""

from typing import Any

from pydantic import ValidationError

from app.config import settings
from app.schemas.repository import (
    Activity,
    AIAnalysis,
    Commit,
    Contributor,
    Issue,
    Metrics,
    PullRequest,
    Quality,
    Release,
    ReleaseDetail,
    Repository,
)
from app.services.ai.client import complete_chat
from app.services.ai.context import build_ai_context
from app.services.ai.exceptions import AIError, AIResponseValidationError

AI_SYSTEM_PROMPT = """Eres un ingeniero de software principal evaluando objetivamente el estado de un repositorio de GitHub.
Tu analisis debe ser exclusivamente tecnico, imparcial y fundamentado 100% en la evidencia real suministrada en el contexto.

REGLAS ESTRICTAS DE ANALISIS:
1. NO inventes metricas, archivos, dependencias, bugs ni vulnerabilidades.
2. Si un dato es null (ej. lines_of_code=null o coverage.configured=False/None), NO asumas valores como 0 o cantidades inventadas; declara con precision que el dato no esta disponible o que no se detecto configuracion en los archivos.
3. No interpretes la ausencia de informacion como evidencia negativa definitiva si el arbol de archivos estuvo truncado (tree_truncated=True) o no disponible.
4. Cada elemento en 'concerns' DEBE incluir una 'evidence' concreta y comprobable extraida directamente de los datos proporcionados.
5. Cada recomendacion en 'recommendations' debe ser accionable, constructiva y coherente con las tecnologias detectadas.
6. Asigna niveles de severidad ('low', 'medium', 'high') y prioridad ('low', 'medium', 'high') con estricta justificacion técnica.
7. Devuelve unicamente un objeto JSON valido con la siguiente estructura:

{
  "summary": "Resumen ejecutivo del estado general del repositorio",
  "strengths": ["Punto fuerte 1 respaldado por datos", "Punto fuerte 2..."],
  "concerns": [
    {
      "title": "Titulo del aspecto a mejorar",
      "description": "Explicacion tecnica del hallazgo",
      "severity": "low | medium | high",
      "evidence": "Cita explicita del dato o metrica que lo demuestra"
    }
  ],
  "recommendations": [
    {
      "title": "Accion recomendada",
      "description": "Detalle concreto de como proceder",
      "priority": "low | medium | high"
    }
  ],
  "technical_overview": {
    "architecture": "Descripcion de la arquitectura deducida de los archivos y directorios",
    "stack": "Lenguajes, herramientas de CI/linting y dependencias principales identificadas",
    "activity_summary": "Evaluacion del ritmo de actividad y mantenimiento segun commits, issues y releases"
  }
}
"""


async def run_ai_analysis(
    repository: Repository,
    languages: dict[str, int],
    contributors: list[Contributor],
    recent_commits: list[Commit],
    issues: list[Issue],
    pull_requests: list[PullRequest],
    releases: list[ReleaseDetail],
    latest_release: Release | None,
    activity: Activity,
    quality: Quality,
    metrics: Metrics,
    *,
    api_key: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
) -> AIAnalysis:
    """Ejecuta el analisis de IA y devuelve el modelo AIAnalysis validado.

    Lanza excepciones de dominio (AIError y derivadas) si ocurre un fallo.
    """
    context = build_ai_context(
        repository=repository,
        languages=languages,
        contributors=contributors,
        recent_commits=recent_commits,
        issues=issues,
        pull_requests=pull_requests,
        releases=releases,
        latest_release=latest_release,
        activity=activity,
        quality=quality,
        metrics=metrics,
    )

    raw_content = await complete_chat(
        system_prompt=AI_SYSTEM_PROMPT,
        user_payload=context,
        api_key=api_key,
        model=model,
        base_url=base_url,
    )

    try:
        return AIAnalysis.model_validate_json(raw_content)
    except ValidationError as error:
        raise AIResponseValidationError(
            f"El JSON devuelto por la IA no cumple con el esquema AIAnalysis: {error}"
        ) from error


async def analyze_with_ai(
    repository: Repository,
    languages: dict[str, int],
    contributors: list[Contributor],
    recent_commits: list[Commit],
    issues: list[Issue],
    pull_requests: list[PullRequest],
    releases: list[ReleaseDetail],
    latest_release: Release | None,
    activity: Activity,
    quality: Quality,
    metrics: Metrics,
) -> AIAnalysis | None:
    """Punto de integracion seguro para el endpoint general de analisis.

    Si la API key no esta configurada o si ocurre cualquier error durante
    el analisis de IA, devuelve None de forma segura sin romper el analisis
    general de GitHub.
    """
    if not settings.ai_api_key or not settings.ai_api_key.strip():
        return None

    try:
        return await run_ai_analysis(
            repository=repository,
            languages=languages,
            contributors=contributors,
            recent_commits=recent_commits,
            issues=issues,
            pull_requests=pull_requests,
            releases=releases,
            latest_release=latest_release,
            activity=activity,
            quality=quality,
            metrics=metrics,
        )
    except AIError:
        return None
    except Exception:
        return None
