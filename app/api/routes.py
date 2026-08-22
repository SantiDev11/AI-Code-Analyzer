"""Capa HTTP: define los endpoints y traduce errores del servicio a codigos HTTP.

Esta capa no sabe hablar con GitHub. Solo recibe la peticion, delega en el
servicio y decide que codigo de estado corresponde a cada error.
"""

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.repository import AnalysisResponse
from app.services import github

router = APIRouter()


@router.get(
    "/analyze/{owner}/{repo}",
    response_model=AnalysisResponse,
    summary="Analiza un repositorio publico de GitHub",
    tags=["analysis"],
)
async def analyze(
    owner: str,
    repo: str,
    commits: int = Query(
        default=github.RECENT_COMMITS_LIMIT,
        ge=1,
        le=github.MAX_RECENT_COMMITS,
        description="Cuantos commits recientes incluir en el analisis",
    ),
) -> AnalysisResponse:
    """Devuelve datos reales del repositorio consultados en la GitHub REST API.

    FastAPI valida `commits` contra los limites declarados y responde 422 por
    su cuenta si el valor se sale del rango, sin que haya que comprobarlo aqui.
    """
    try:
        return await github.analyze_repository(owner, repo, commits_limit=commits)

    except github.RepositoryNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repositorio '{owner}/{repo}' no encontrado: {error}",
        ) from error

    except github.RateLimitExceeded as error:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(error),
        ) from error

    except github.GitHubUnavailable as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error

    except github.GitHubError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Respuesta inesperada de GitHub: {error}",
        ) from error
