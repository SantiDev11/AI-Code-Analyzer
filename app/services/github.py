"""Comunicacion con la GitHub REST API.

Esta capa es la unica que conoce httpx y el formato de GitHub. No importa
FastAPI: en lugar de devolver errores HTTP, lanza excepciones propias que la
capa de rutas traducira despues.
"""

import asyncio
from datetime import UTC, date, datetime, timedelta

import httpx
from pydantic import ValidationError

from app.config import settings
from app.schemas.repository import (
    Activity,
    AnalysisResponse,
    Commit,
    Contributor,
    DailyActivity,
    Issue,
    Metrics,
    PullRequest,
    Quality,
    Release,
    ReleaseDetail,
    Repository,
)
from app.services.ai import analyze_with_ai
from app.services.cache import TTLCache
from app.services.metrics import TreeEntry, analyze_metrics
from app.services.quality import analyze_quality

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

# Lo mismo para los pull requests. Comparten tope con lo demas por la misma
# razon: GitHub no sirve mas de 100 por pagina.
PULL_REQUESTS_LIMIT = 10
MAX_PULL_REQUESTS = 100

# Y lo mismo para el historial de releases.
RELEASES_LIMIT = 10
MAX_RELEASES = 100

# Ventana del analisis de actividad, en dias naturales UTC contando hoy. El
# valor por defecto es configurable con ACTIVITY_DAYS; el tope evita periodos
# absurdos, no hay datos con los que llenarlos.
ACTIVITY_DAYS = settings.activity_days
MAX_ACTIVITY_DAYS = 365

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


def _utc_now() -> datetime:
    """Instante actual en UTC.

    Existe como funcion propia para que los tests puedan sustituirla y no
    dependan del dia en que se ejecuten, igual que TTLCache admite un reloj.
    """
    return datetime.now(UTC)


def _utc_date(momento: datetime | None) -> date | None:
    """Dia UTC de un instante, o None si no hay fecha.

    GitHub publica sus timestamps en UTC y pydantic los convierte en datetime
    con zona horaria. Si alguno llegara sin zona lo tratamos como UTC en vez
    de suponer la hora local de la maquina: agrupar por hora local haria que
    el mismo repositorio diera resultados distintos segun donde corra esto.
    """
    if momento is None:
        return None
    if momento.tzinfo is None:
        return momento.date()
    return momento.astimezone(UTC).date()


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


async def _fetch_releases(
    client: httpx.AsyncClient, owner: str, repo: str, limit: int
) -> list[ReleaseDetail]:
    """GET /repos/{owner}/{repo}/releases -> historial de versiones.

    Convive con _fetch_latest_release sin sustituirlo: aquel pregunta por la
    ultima version publicada a /releases/latest, que ignora los borradores.

    Aqui no se ordena nada. GitHub ya devuelve la lista del mas reciente al
    mas antiguo, y no hay un criterio mejor que imponer: los borradores no
    tienen fecha de publicacion con la que compararlos.

    Tampoco hay excepcion para el 404, a diferencia de /releases/latest, donde
    significa que el repositorio no tiene ninguna version. En esta lista un
    repositorio sin releases responde 200 con lista vacia, asi que un 404 es
    un repositorio que no existe.
    """
    response = await client.get(
        f"/repos/{owner}/{repo}/releases", params={"per_page": limit}
    )

    _raise_for_status(response)
    return _to_releases(response.json())


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


async def _fetch_pull_requests(
    client: httpx.AsyncClient, owner: str, repo: str, limit: int
) -> list[PullRequest]:
    """GET /repos/{owner}/{repo}/pulls -> pull requests abiertos y cerrados.

    Se consulta este endpoint y no /issues, aunque GitHub sirva los pull
    requests por los dos: solo aqui vienen la fecha de merge y las ramas.

    state=all hace falta por lo mismo que en los issues: por defecto GitHub
    devuelve solo los abiertos, y sin los cerrados no habria nada que contar.
    sort y direction piden ya en el servidor el orden que prometemos, para no
    traernos los diez mas antiguos y ordenarlos despues.

    Aqui no hay excepcion para el 404, a diferencia de /issues: los issues se
    pueden desactivar en un repositorio, los pull requests no. Un repositorio
    sin ninguno responde 200 con lista vacia, asi que un 404 significa de
    verdad que el repositorio no existe.
    """
    response = await client.get(
        f"/repos/{owner}/{repo}/pulls",
        params={
            "per_page": limit,
            "state": "all",
            "sort": "created",
            "direction": "desc",
        },
    )

    _raise_for_status(response)
    return _to_pull_requests(response.json())


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


async def _fetch_tree(
    client: httpx.AsyncClient, owner: str, repo: str, default_branch: str | None
) -> tuple[list[TreeEntry], bool, bool]:
    """GET /repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1

    Devuelve (entries, available, truncated).
    Consulta el arbol de archivos de la rama por defecto sin ejecutar nada del
    repositorio ni descargar dependencias o contenidos de archivos.
    """
    if not default_branch:
        return [], False, False

    response = await client.get(
        f"/repos/{owner}/{repo}/git/trees/{default_branch}",
        params={"recursive": "1"},
    )

    # 404/409: arbol no encontrado o repositorio vacio sin commits.
    if response.status_code in (404, 409):
        return [], False, False

    is_rate_limited = response.headers.get("X-RateLimit-Remaining") == "0"
    if response.status_code in (403, 429) and is_rate_limited:
        raise RateLimitExceeded(
            "Cuota de la GitHub API agotada. Configura GITHUB_TOKEN para ampliarla"
        )

    if not response.is_success:
        return [], False, False

    try:
        data = response.json()
        tree_items = data.get("tree", [])
        entries = [
            TreeEntry(
                path=item["path"],
                type=item.get("type", "blob"),
                size=item.get("size"),
            )
            for item in tree_items
            if isinstance(item, dict) and "path" in item
        ]
        truncated = bool(data.get("truncated", False))
        return entries, True, truncated
    except Exception:
        return [], False, False


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


def _to_releases(data: object) -> list[ReleaseDetail]:
    """Traduce el historial de releases respetando el orden de GitHub.

    Los campos que GitHub deja sin informar (titulo, notas, autor, fecha de
    publicacion) se leen con cuidado: que a un release le falte uno no puede
    tumbar el analisis entero.
    """
    try:
        return [
            ReleaseDetail(
                id=item["id"],
                tag_name=item["tag_name"],
                name=item.get("name"),
                body=item.get("body"),
                draft=item["draft"],
                prerelease=item["prerelease"],
                created_at=item["created_at"],
                # Null mientras sea un borrador. Es la fecha de publicacion
                # real, distinta de created_at, que existe desde el principio.
                published_at=item.get("published_at"),
                # "author" es quien lo publico; null si la cuenta fue borrada.
                author=(item.get("author") or {}).get("login"),
                url=item["html_url"],
            )
            for item in data
        ]
    except (TypeError, KeyError, ValidationError) as error:
        raise GitHubError(
            f"Lista de releases con un formato inesperado: {error}"
        ) from error


def _to_pull_requests(data: object) -> list[PullRequest]:
    """Traduce los pull requests de GitHub, del mas reciente al mas antiguo.

    GitHub ya los manda en ese orden porque se lo hemos pedido, pero no lo
    damos por hecho: el orden es parte de nuestro contrato, igual que en los
    contribuidores, asi que lo garantizamos aqui.

    Los campos que GitHub puede dejar sin informar (autor, ramas, fecha de
    merge) se leen con cuidado: que a un pull request le falte uno no puede
    tumbar el analisis entero.
    """
    try:
        pull_requests = [
            PullRequest(
                number=item["number"],
                title=item["title"],
                state=item["state"],
                # "user" es quien lo abrio; null si la cuenta fue borrada.
                author=(item.get("user") or {}).get("login"),
                created_at=item["created_at"],
                updated_at=item["updated_at"],
                # Null mientras siga abierto. Un pull request cerrado sin
                # mergear tiene closed_at pero no merged_at, asi que hacen
                # falta los dos para contar cierres sin quedarse corto.
                closed_at=item.get("closed_at"),
                # En el listado de GitHub esta fecha es el unico rastro del
                # merge: el campo "merged" solo existe pidiendo el pull
                # request de uno en uno.
                merged_at=item.get("merged_at"),
                # head.repo llega null si el fork de origen se borro, pero
                # head.ref sobrevive. Aun asi lo leemos sin dar nada por hecho.
                source_branch=(item.get("head") or {}).get("ref"),
                target_branch=(item.get("base") or {}).get("ref"),
                url=item["html_url"],
            )
            for item in data
        ]
    except (TypeError, KeyError, ValidationError) as error:
        raise GitHubError(
            f"Lista de pull requests con un formato inesperado: {error}"
        ) from error

    return sorted(pull_requests, key=lambda pr: pr.created_at, reverse=True)


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


# Los recuentos que lleva cada dia, en el orden en que se declaran.
_CAMPOS_DIARIOS = (
    "commits",
    "issues",
    "pull_requests_opened",
    "pull_requests_closed",
    "releases",
)


def _build_activity(
    commits: list[Commit],
    issues: list[Issue],
    pull_requests: list[PullRequest],
    releases: list[ReleaseDetail],
    days: int,
    now: datetime,
) -> Activity:
    """Reparte por dia la actividad que ya hemos descargado.

    No consulta GitHub: reaprovecha las cuatro listas del analisis. Por eso
    los totales describen la muestra analizada dentro del periodo, no todo lo
    que ocurrio de verdad en el repositorio.

    Los borradores de release no cuentan: su published_at es null porque no
    llegaron a publicarse nunca.
    """
    until = _utc_date(now)
    since = until - timedelta(days=days - 1)

    diario: dict[date, dict[str, int]] = {}

    def anota(momento: datetime | None, campo: str) -> None:
        dia = _utc_date(momento)
        if dia is None or dia < since or dia > until:
            return
        recuento = diario.setdefault(dia, dict.fromkeys(_CAMPOS_DIARIOS, 0))
        recuento[campo] += 1

    for commit in commits:
        anota(commit.date, "commits")
    for issue in issues:
        anota(issue.created_at, "issues")
    for pull_request in pull_requests:
        anota(pull_request.created_at, "pull_requests_opened")
        anota(pull_request.closed_at, "pull_requests_closed")
    for release in releases:
        anota(release.published_at, "releases")

    daily = [
        DailyActivity(date=dia, **recuento)
        for dia, recuento in sorted(diario.items(), reverse=True)
    ]

    # Los totales salen de sumar los dias, no de recorrer las listas otra vez:
    # asi no pueden acabar contando cosas distintas.
    return Activity(
        days=days,
        since=since,
        until=until,
        total_commits=sum(dia.commits for dia in daily),
        total_issues=sum(dia.issues for dia in daily),
        total_pull_requests=sum(dia.pull_requests_opened for dia in daily),
        total_releases=sum(dia.releases for dia in daily),
        daily=daily,
    )


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
        default_branch=data.get("default_branch", "main"),
    )


def _cache_key(
    owner: str,
    repo: str,
    commits_limit: int,
    issues_limit: int,
    pulls_limit: int,
    releases_limit: int,
    activity_days: int,
) -> str:
    """Clave de cache. GitHub no distingue mayusculas en owner ni en repo.

    Los limites forman parte de la clave: pedir 30 commits despues de pedir 10
    debe volver a consultar GitHub, no reutilizar la respuesta corta. Cada
    limite que el usuario puede elegir tiene que aparecer aqui.
    """
    return (
        f"{owner.lower()}/{repo.lower()}"
        f"#commits={commits_limit}#issues={issues_limit}"
        f"#pulls={pulls_limit}#releases={releases_limit}"
        f"#days={activity_days}"
    )


async def analyze_repository(
    owner: str,
    repo: str,
    commits_limit: int = RECENT_COMMITS_LIMIT,
    issues_limit: int = ISSUES_LIMIT,
    pulls_limit: int = PULL_REQUESTS_LIMIT,
    releases_limit: int = RELEASES_LIMIT,
    activity_days: int = ACTIVITY_DAYS,
) -> AnalysisResponse:
    """Devuelve el analisis completo del repositorio.

    Si el mismo repositorio se consulto hace poco, se reutiliza el resultado
    guardado en cache y no se llama a GitHub.

    Las peticiones iniciales son independientes entre si, por lo que se lanzan
    en paralelo. Despues se consulta el arbol de archivos de la rama por
    defecto obtenida de la metadata para deducir las senales de calidad.
    """
    key = _cache_key(
        owner,
        repo,
        commits_limit,
        issues_limit,
        pulls_limit,
        releases_limit,
        activity_days,
    )

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
                pull_requests,
                releases,
            ) = await asyncio.gather(
                _fetch_repository(client, owner, repo),
                _fetch_languages(client, owner, repo),
                _fetch_contributors(client, owner, repo),
                _fetch_latest_release(client, owner, repo),
                _fetch_recent_commits(client, owner, repo, commits_limit),
                _fetch_issues(client, owner, repo, issues_limit),
                _fetch_pull_requests(client, owner, repo, pulls_limit),
                _fetch_releases(client, owner, repo, releases_limit),
            )

            default_branch = repository_data.get("default_branch")
            entries, tree_available, tree_truncated = await _fetch_tree(
                client, owner, repo, default_branch
            )
        except httpx.TimeoutException as error:
            raise GitHubUnavailable("GitHub ha tardado demasiado en responder") from error
        except httpx.RequestError as error:
            raise GitHubUnavailable("No se ha podido conectar con GitHub") from error

    blob_paths = [e.path for e in entries if e.type == "blob"]
    quality = analyze_quality(
        blob_paths, available=tree_available, truncated=tree_truncated
    )
    metrics = analyze_metrics(
        entries, available=tree_available, truncated=tree_truncated
    )

    repository = _to_repository(repository_data)
    activity = _build_activity(
        recent_commits,
        issues,
        pull_requests,
        releases,
        activity_days,
        _utc_now(),
    )

    ai_analysis = await analyze_with_ai(
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

    result = AnalysisResponse(
        repository=repository,
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
        pull_requests=pull_requests,
        # Abierto y cerrado son excluyentes; mergeado no es un tercer estado,
        # sino algo que le pasa a uno cerrado. Por eso un pull request
        # mergeado suma en los cerrados y en los mergeados a la vez, y por eso
        # el merge se mira por merged_at y no por state.
        pull_requests_count=len(pull_requests),
        open_pull_requests_count=sum(
            1 for pr in pull_requests if pr.state == "open"
        ),
        closed_pull_requests_count=sum(
            1 for pr in pull_requests if pr.state == "closed"
        ),
        merged_pull_requests_count=sum(
            1 for pr in pull_requests if pr.merged_at is not None
        ),
        releases=releases,
        # draft y prerelease tampoco son estados excluyentes. Publicado es
        # exactamente "no es un borrador": GitHub deja published_at en null
        # mientras lo sea. Una version previa publicada cuenta a la vez en
        # published y en prereleases, igual que un pull request mergeado
        # cuenta a la vez en cerrados y en mergeados.
        releases_count=len(releases),
        published_releases_count=sum(1 for r in releases if not r.draft),
        draft_releases_count=sum(1 for r in releases if r.draft),
        prereleases_count=sum(1 for r in releases if r.prerelease),
        # Sin peticiones extra: la actividad se deduce de las cuatro listas
        # que acabamos de traer.
        activity=activity,
        quality=quality,
        metrics=metrics,
        ai_analysis=ai_analysis,
    )
    _cache.set(key, result)
    return result
