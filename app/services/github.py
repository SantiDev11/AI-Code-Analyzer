"""Comunicacion con la GitHub REST API.

Esta capa es la unica que conoce httpx y el formato de GitHub. No importa
FastAPI: en lugar de devolver errores HTTP, lanza excepciones propias que la
capa de rutas traducira despues.
"""

import asyncio

import httpx
from pydantic import ValidationError

from app.config import settings
from app.schemas.repository import (
    AnalysisResponse,
    Commit,
    Contributor,
    Issue,
    Release,
    Repository,
)
from app.services.cache import TTLCache

API_BASE = "https://api.github.com"
TIMEOUT = httpx.Timeout(10.0)

# Cuantos commits recientes se incluyen si no se pide otra cosa.
RECENT_COMMITS_LIMIT = 10

# Tope admitido. GitHub no sirve mas de 100 por pagina, asi que pedir mas no
# devolveria commits adicionales: solo gastaria cuota.
MAX_RECENT_COMMITS = 100

# Cuantos issues se analizan si no se pide otra cosa, y el tope admitido.
ISSUES_LIMIT = 10
MAX_ISSUES = 100

# Cuantos contribuidores se incluyen. GitHub los devuelve ya ordenados de mas a
# menos contribuciones, asi que la primera pagina es directamente el top.
CONTRIBUTORS_LIMIT = 10

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


async def _fetch_contributors(
    client: httpx.AsyncClient, owner: str, repo: str
) -> list[Contributor]:
    """GET /repos/{owner}/{repo}/contributors -> los que mas han contribuido.

    A diferencia del conteo, aqui no se pide anon=true: un contribuidor
    anonimo es un correo sin cuenta de GitHub asociada, no tiene usuario ni
    avatar ni perfil, y no podria representarse con nuestro modelo.
    """
    response = await client.get(
        f"/repos/{owner}/{repo}/contributors",
        params={"per_page": CONTRIBUTORS_LIMIT},
    )

    # 204 No Content: repositorio vacio, sin commits.
    if response.status_code == 204:
        return []

    # Historial demasiado grande para que GitHub lo calcule. El conteo devuelve
    # null en este caso; aqui la lista vacia es la respuesta honesta.
    if response.status_code == 403 and _is_contributor_list_too_large(response):
        return []

    _raise_for_status(response)
    return _to_contributors(response.json())


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


async def _fetch_issues(
    client: httpx.AsyncClient, owner: str, repo: str, limit: int
) -> list[Issue]:
    """GET /repos/{owner}/{repo}/issues -> issues abiertos y cerrados.

    Hace falta state=all porque GitHub devuelve solo los abiertos por defecto,
    y sin los cerrados el recuento de cerrados seria siempre cero.

    Un 404 o un 410 aqui NO significan que el repositorio no exista: es lo que
    responde GitHub cuando el repositorio tiene los issues desactivados. La
    lista vacia es la respuesta correcta. Si de verdad no existiera, la llamada
    a /repos lo detectaria y lanzaria RepositoryNotFound.
    """
    response = await client.get(
        f"/repos/{owner}/{repo}/issues",
        params={"per_page": limit, "state": "all"},
    )

    if response.status_code in (404, 410):
        return []

    _raise_for_status(response)
    return _to_issues(response.json())


async def _fetch_recent_commits(
    client: httpx.AsyncClient, owner: str, repo: str, limit: int
) -> list[Commit]:
    """GET /repos/{owner}/{repo}/commits -> ultimos commits de la rama principal.

    Un repositorio sin commits responde 409 Conflict; en ese caso la lista
    correcta es la vacia, no un error.
    """
    response = await client.get(
        f"/repos/{owner}/{repo}/commits", params={"per_page": limit}
    )

    if response.status_code == 409:
        return []

    _raise_for_status(response)
    return _to_commits(response.json())


# --------------------------------------------------------------------------
# API publica del servicio
# --------------------------------------------------------------------------


def _to_commit(data: dict) -> Commit:
    """Traduce un commit de GitHub a nuestro modelo Commit."""
    commit = data["commit"]
    # data["author"] es la cuenta de GitHub y puede ser null si el correo del
    # commit no esta asociado a ningun usuario; commit["author"] guarda el
    # nombre y la fecha que quedaron escritos en el propio commit.
    cuenta = data.get("author") or {}
    firma = commit.get("author") or {}

    # Un mensaje vacio es legal en git, asi que splitlines() puede no devolver
    # ninguna linea.
    lineas = commit["message"].splitlines()

    return Commit(
        sha=data["sha"][:7],
        message=lineas[0] if lineas else "",
        # Sin cuenta y sin nombre firmado no hay autor que publicar: null antes
        # que inventarlo.
        author=cuenta.get("login") or firma.get("name"),
        date=firma["date"],
        url=data["html_url"],
    )


def _es_pull_request(item: object) -> bool:
    """True si el elemento es un pull request y no un issue.

    GitHub sirve ambos por /issues. El unico distintivo fiable es la clave
    "pull_request", que solo aparece en los pull requests.
    """
    return isinstance(item, dict) and "pull_request" in item


def _to_issues(data: object) -> list[Issue]:
    """Traduce los issues de GitHub, descartando los pull requests.

    Si la respuesta no tiene la forma esperada preferimos un error controlado
    (que la capa de rutas traduce a 502) antes que un fallo interno.
    """
    try:
        return [
            Issue(
                number=item["number"],
                title=item["title"],
                state=item["state"],
                # "user" es quien lo abrio; GitHub lo manda null si la cuenta
                # fue borrada. Sin cuenta no hay autor: null antes que inventar.
                author=(item.get("user") or {}).get("login"),
                created_at=item["created_at"],
                updated_at=item["updated_at"],
                url=item["html_url"],
            )
            for item in data
            if not _es_pull_request(item)
        ]
    except (TypeError, KeyError, ValidationError) as error:
        raise GitHubError(
            f"Lista de issues con un formato inesperado: {error}"
        ) from error


def _to_commits(data: object) -> list[Commit]:
    """Traduce la lista de commits de GitHub.

    Si a un commit le falta la fecha, o la respuesta no tiene la forma que
    esperamos, preferimos un error controlado (que la capa de rutas traduce a
    502) antes que un fallo interno del servidor.
    """
    try:
        return [_to_commit(item) for item in data]
    except (TypeError, KeyError, ValidationError) as error:
        raise GitHubError(
            f"Lista de commits con un formato inesperado: {error}"
        ) from error


def _tiene_usuario(item: object) -> bool:
    """True si el contribuidor tiene una cuenta de GitHub identificable."""
    return isinstance(item, dict) and bool(item.get("login"))


def _to_contributors(data: object) -> list[Contributor]:
    """Traduce la lista de GitHub a nuestro modelo y la ordena.

    GitHub ya la manda de mas a menos contribuciones, pero no lo damos por
    hecho: el orden es parte de nuestro contrato, asi que lo garantizamos.

    Los contribuidores sin cuenta de GitHub se descartan: no tienen usuario,
    avatar ni perfil, asi que no hay nada que publicar de ellos. Descartar uno
    no invalida el resto de la lista.

    Si la respuesta no tiene la forma esperada preferimos un error controlado
    (que la capa de rutas traduce a 502) antes que un fallo interno.
    """
    try:
        contributors = [
            Contributor(
                username=item["login"],
                contributions=item["contributions"],
                avatar_url=item["avatar_url"],
                profile_url=item["html_url"],
            )
            for item in data
            if _tiene_usuario(item)
        ]
    except (TypeError, KeyError, ValidationError) as error:
        raise GitHubError(
            f"Lista de contribuidores con un formato inesperado: {error}"
        ) from error

    return sorted(contributors, key=lambda person: person.contributions, reverse=True)


def _to_repository(data: dict) -> Repository:
    """Traduce la respuesta de GitHub a nuestro modelo Repository."""
    return Repository(
        name=data["name"],
        full_name=data["full_name"],
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


def _cache_key(
    owner: str, repo: str, commits_limit: int, issues_limit: int
) -> str:
    """Clave de cache. GitHub no distingue mayusculas en owner ni en repo.

    Los limites forman parte de la clave: pedir 30 commits despues de pedir 10
    debe volver a consultar GitHub, no reutilizar la respuesta corta. Cada
    limite que el usuario puede elegir tiene que aparecer aqui.
    """
    return (
        f"{owner.lower()}/{repo.lower()}"
        f"#commits={commits_limit}#issues={issues_limit}"
    )


async def analyze_repository(
    owner: str,
    repo: str,
    commits_limit: int = RECENT_COMMITS_LIMIT,
    issues_limit: int = ISSUES_LIMIT,
) -> AnalysisResponse:
    """Devuelve el analisis completo del repositorio.

    Si el mismo repositorio se consulto hace poco, se reutiliza el resultado
    guardado en cache y no se llama a GitHub.

    Las seis peticiones son independientes entre si, por lo que se lanzan en
    paralelo: el tiempo total es el de la mas lenta, no la suma de las seis.
    """
    key = _cache_key(owner, repo, commits_limit, issues_limit)

    cached_result = _cache.get(key)
    if cached_result is not None:
        # Copia marcada como cacheada; la guardada conserva cached=False.
        return cached_result.model_copy(update={"cached": True})

    async with _create_client() as client:
        try:
            (
                repository_data,
                languages,
                contributors,
                latest_release,
                recent_commits,
                issues,
            ) = await asyncio.gather(
                _fetch_repository(client, owner, repo),
                _fetch_languages(client, owner, repo),
                _fetch_contributors(client, owner, repo),
                _fetch_latest_release(client, owner, repo),
                _fetch_recent_commits(client, owner, repo, commits_limit),
                _fetch_issues(client, owner, repo, issues_limit),
            )
        except httpx.TimeoutException as error:
            raise GitHubUnavailable("GitHub ha tardado demasiado en responder") from error
        except httpx.RequestError as error:
            raise GitHubUnavailable("No se ha podido conectar con GitHub") from error

    result = AnalysisResponse(
        repository=_to_repository(repository_data),
        languages=languages,
        contributors=contributors,
        contributors_count=len(contributors),
        latest_release=latest_release,
        recent_commits=recent_commits,
        issues=issues,
        # Los contadores describen los issues que hemos analizado, ya sin
        # pull requests, asi que abiertos + cerrados siempre suman el total.
        issues_count=len(issues),
        open_issues_count=sum(1 for issue in issues if issue.state == "open"),
        closed_issues_count=sum(1 for issue in issues if issue.state == "closed"),
    )
    _cache.set(key, result)
    return result
