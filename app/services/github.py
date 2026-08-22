"""Comunicacion con la GitHub REST API.

Esta capa es la unica que conoce httpx y el formato de GitHub. No importa
FastAPI: en lugar de devolver errores HTTP, lanza excepciones propias que la
capa de rutas traducira despues.
"""

import asyncio

import httpx

from app.config import settings
from app.schemas.repository import AnalysisResponse, Commit, Release, Repository
from app.services.cache import TTLCache

API_BASE = "https://api.github.com"
TIMEOUT = httpx.Timeout(10.0)

# Cuantos commits recientes se incluyen en el analisis.
RECENT_COMMITS_LIMIT = 5

# Analisis ya calculados, reutilizados durante settings.cache_ttl_seconds.
_cache: TTLCache[AnalysisResponse] = TTLCache(ttl_seconds=settings.cache_ttl_seconds)


# --------------------------------------------------------------------------
# Excepciones propias del dominio
# --------------------------------------------------------------------------


class GitHubError(Exception):
    """Error generico al comunicarse con GitHub."""


class RepositoryNotFound(GitHubError):
    """El repositorio no existe o es privado."""


class RateLimitExceeded(GitHubError):
    """Se ha agotado la cuota de peticiones de la GitHub API."""


class GitHubUnavailable(GitHubError):
    """GitHub no responde: timeout o fallo de red."""


# --------------------------------------------------------------------------
# Utilidades internas
# --------------------------------------------------------------------------


def _build_headers() -> dict[str, str]:
    """Cabeceras exigidas por GitHub, mas autenticacion si hay token."""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"
    return headers


def _create_client() -> httpx.AsyncClient:
    """Crea el cliente HTTP usado para hablar con GitHub.

    Esta funcion existe como punto de sustitucion: los tests la reemplazan
    por un cliente con respuestas simuladas, sin tocar la red.
    """
    return httpx.AsyncClient(
        base_url=API_BASE, headers=_build_headers(), timeout=TIMEOUT
    )


def _raise_for_status(response: httpx.Response) -> None:
    """Traduce un codigo de error de GitHub a una excepcion propia."""
    if response.is_success:
        return

    if response.status_code == 404:
        raise RepositoryNotFound("El repositorio no existe o no es publico")

    is_rate_limited = response.headers.get("X-RateLimit-Remaining") == "0"
    if response.status_code in (403, 429) and is_rate_limited:
        raise RateLimitExceeded(
            "Cuota de la GitHub API agotada. Configura GITHUB_TOKEN para ampliarla"
        )

    raise GitHubError(f"GitHub respondio {response.status_code}")


def _is_contributor_list_too_large(response: httpx.Response) -> bool:
    """Detecta el 403 que GitHub devuelve en repositorios demasiado grandes."""
    try:
        message = response.json().get("message", "")
    except ValueError:
        return False
    return "too large" in message


def _extract_last_page(link_header: str) -> int | None:
    """Devuelve el numero de la ultima pagina indicado en la cabecera 'Link'.

    GitHub pagina con una cabecera con este aspecto:
        <...&page=2>; rel="next", <...&page=87>; rel="last"
    Nos interesa unicamente el valor de 'page' del enlace rel="last".
    """
    for link in link_header.split(","):
        parts = link.split(";")
        if len(parts) < 2:
            continue
        if not any('rel="last"' in part for part in parts[1:]):
            continue
        url = httpx.URL(parts[0].strip().strip("<>"))
        page = url.params.get("page")
        return int(page) if page else None
    return None


# --------------------------------------------------------------------------
# Llamadas a la API (una funcion por endpoint de GitHub)
# --------------------------------------------------------------------------


async def _fetch_repository(
    client: httpx.AsyncClient, owner: str, repo: str
) -> dict:
    """GET /repos/{owner}/{repo} -> datos generales del repositorio."""
    response = await client.get(f"/repos/{owner}/{repo}")
    _raise_for_status(response)
    return response.json()


async def _fetch_languages(
    client: httpx.AsyncClient, owner: str, repo: str
) -> dict[str, int]:
    """GET /repos/{owner}/{repo}/languages -> {"Python": 12345, ...}."""
    response = await client.get(f"/repos/{owner}/{repo}/languages")
    _raise_for_status(response)
    return response.json()


async def _fetch_contributors_count(
    client: httpx.AsyncClient, owner: str, repo: str
) -> int | None:
    """Numero de contribuidores, sin recorrer todas las paginas.

    Pedimos un unico contribuidor por pagina: asi el numero de la ultima
    pagina equivale al total de contribuidores y basta una sola peticion.

    Devuelve None si GitHub se niega a calcularlo. En repositorios con un
    historial enorme (por ejemplo torvalds/linux) responde 403 con el
    mensaje "contributor list is too large"; no es un fallo de cuota, asi
    que preferimos devolver null antes que inventar un numero.
    """
    response = await client.get(
        f"/repos/{owner}/{repo}/contributors",
        params={"per_page": 1, "anon": "true"},
    )

    # 204 No Content: repositorio vacio, sin commits.
    if response.status_code == 204:
        return 0

    if response.status_code == 403 and _is_contributor_list_too_large(response):
        return None

    _raise_for_status(response)

    last_page = _extract_last_page(response.headers.get("Link", ""))
    if last_page is not None:
        return last_page

    # Sin cabecera Link solo hay una pagina: contamos sus elementos (0 o 1).
    return len(response.json())


async def _fetch_latest_release(
    client: httpx.AsyncClient, owner: str, repo: str
) -> Release | None:
    """GET /repos/{owner}/{repo}/releases/latest -> ultima version publicada.

    Devuelve None si el repositorio no tiene ninguna release. Aqui un 404 NO
    significa que el repositorio no exista: significa que no hay releases, asi
    que se trata antes de la comprobacion general de errores.
    """
    response = await client.get(f"/repos/{owner}/{repo}/releases/latest")

    if response.status_code == 404:
        return None

    _raise_for_status(response)
    data = response.json()
    return Release(
        tag=data["tag_name"],
        name=data["name"],
        published_at=data["published_at"],
        url=data["html_url"],
    )


async def _fetch_recent_commits(
    client: httpx.AsyncClient, owner: str, repo: str
) -> list[Commit]:
    """GET /repos/{owner}/{repo}/commits -> ultimos commits de la rama principal.

    Un repositorio sin commits responde 409 Conflict; en ese caso la lista
    correcta es la vacia, no un error.
    """
    response = await client.get(
        f"/repos/{owner}/{repo}/commits", params={"per_page": RECENT_COMMITS_LIMIT}
    )

    if response.status_code == 409:
        return []

    _raise_for_status(response)
    return [_to_commit(item) for item in response.json()]


# --------------------------------------------------------------------------
# API publica del servicio
# --------------------------------------------------------------------------


def _to_commit(data: dict) -> Commit:
    """Traduce un commit de GitHub a nuestro modelo Commit."""
    commit = data["commit"]
    # data["author"] es la cuenta de GitHub y puede ser null si el correo del
    # commit no esta asociado a ningun usuario; commit["author"]["name"] es el
    # nombre que quedo escrito en el propio commit y siempre existe.
    author = data.get("author") or {}
    return Commit(
        sha=data["sha"][:7],
        message=commit["message"].splitlines()[0],
        author=author.get("login") or commit["author"]["name"],
        date=commit["author"]["date"],
        url=data["html_url"],
    )


def _to_repository(data: dict) -> Repository:
    """Traduce la respuesta de GitHub a nuestro modelo Repository."""
    return Repository(
        name=data["name"],
        description=data["description"],
        stars=data["stargazers_count"],
        forks=data["forks_count"],
        open_issues=data["open_issues_count"],
        created_at=data["created_at"],
        updated_at=data["updated_at"],
        primary_language=data["language"],
        url=data["html_url"],
        license=(data["license"] or {}).get("spdx_id"),
        topics=data.get("topics", []),
        size_kb=data["size"],
        is_archived=data["archived"],
    )


def _cache_key(owner: str, repo: str) -> str:
    """Clave de cache. GitHub no distingue mayusculas en owner ni en repo."""
    return f"{owner.lower()}/{repo.lower()}"


async def analyze_repository(owner: str, repo: str) -> AnalysisResponse:
    """Devuelve el analisis completo del repositorio.

    Si el mismo repositorio se consulto hace poco, se reutiliza el resultado
    guardado en cache y no se llama a GitHub.

    Las cinco peticiones son independientes entre si, por lo que se lanzan en
    paralelo: el tiempo total es el de la mas lenta, no la suma de las cinco.
    """
    key = _cache_key(owner, repo)

    cached_result = _cache.get(key)
    if cached_result is not None:
        # Copia marcada como cacheada; la guardada conserva cached=False.
        return cached_result.model_copy(update={"cached": True})

    async with _create_client() as client:
        try:
            (
                repository_data,
                languages,
                contributors_count,
                latest_release,
                recent_commits,
            ) = await asyncio.gather(
                _fetch_repository(client, owner, repo),
                _fetch_languages(client, owner, repo),
                _fetch_contributors_count(client, owner, repo),
                _fetch_latest_release(client, owner, repo),
                _fetch_recent_commits(client, owner, repo),
            )
        except httpx.TimeoutException as error:
            raise GitHubUnavailable("GitHub ha tardado demasiado en responder") from error
        except httpx.RequestError as error:
            raise GitHubUnavailable("No se ha podido conectar con GitHub") from error

    result = AnalysisResponse(
        repository=_to_repository(repository_data),
        languages=languages,
        contributors_count=contributors_count,
        latest_release=latest_release,
        recent_commits=recent_commits,
    )
    _cache.set(key, result)
    return result
