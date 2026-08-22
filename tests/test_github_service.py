"""Tests de la capa de servicio: traduccion de datos y manejo de errores."""

import httpx
import pytest

from app.services import github
from tests.conftest import (
    COMMITS_PAYLOAD,
    LANGUAGES_PAYLOAD,
    REPO_PAYLOAD,
    is_repository_endpoint,
    successful_handler,
)


async def test_analiza_repositorio_correctamente(fake_github):
    """El caso feliz: los tres endpoints responden y se combinan bien."""
    fake_github(successful_handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.repository.name == REPO_PAYLOAD["name"]
    assert result.repository.full_name == REPO_PAYLOAD["full_name"]
    assert result.repository.stars == REPO_PAYLOAD["stargazers_count"]
    assert result.repository.forks == REPO_PAYLOAD["forks_count"]
    assert result.repository.open_issues == REPO_PAYLOAD["open_issues_count"]
    assert result.repository.primary_language == REPO_PAYLOAD["language"]
    assert result.repository.url == REPO_PAYLOAD["html_url"]
    assert result.languages == LANGUAGES_PAYLOAD
    assert result.contributors_count == len(result.contributors)


async def test_repositorio_inexistente_lanza_not_found(fake_github):
    fake_github(lambda request: httpx.Response(404, json={"message": "Not Found"}))

    with pytest.raises(github.RepositoryNotFound):
        await github.analyze_repository("SantiDev11", "no-existe")


async def test_cuota_agotada_lanza_rate_limit(fake_github):
    """GitHub devuelve 403 con X-RateLimit-Remaining a 0 cuando agotas la cuota."""
    fake_github(
        lambda request: httpx.Response(
            403,
            json={"message": "API rate limit exceeded"},
            headers={"X-RateLimit-Remaining": "0"},
        )
    )

    with pytest.raises(github.RateLimitExceeded):
        await github.analyze_repository("encode", "httpx")


async def test_lista_de_contributors_demasiado_grande_no_es_error(fake_github):
    """Un 403 por historial enorme NO es falta de cuota: devolvemos lista vacia."""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/contributors"):
            return httpx.Response(
                403,
                json={"message": "The contributor list is too large to list ..."},
                headers={"X-RateLimit-Remaining": "47"},
            )
        return successful_handler(request)

    fake_github(handler)

    result = await github.analyze_repository("torvalds", "linux")

    assert result.contributors == []
    assert result.contributors_count == 0
    assert result.repository.name == REPO_PAYLOAD["name"]


async def test_repositorio_vacio_devuelve_cero_contributors(fake_github):
    """Sin commits, GitHub responde 204 No Content."""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/contributors"):
            return httpx.Response(204)
        return successful_handler(request)

    fake_github(handler)

    result = await github.analyze_repository("alguien", "repo-vacio")

    assert result.contributors_count == 0


async def test_campos_ausentes_se_mantienen_null(fake_github):
    """No inventamos datos: si GitHub manda null, devolvemos null."""

    def handler(request: httpx.Request) -> httpx.Response:
        if not is_repository_endpoint(request):
            return successful_handler(request)
        return httpx.Response(
            200, json={**REPO_PAYLOAD, "description": None, "language": None}
        )

    fake_github(handler)

    result = await github.analyze_repository("octocat", "Hello-World")

    assert result.repository.description is None
    assert result.repository.primary_language is None


async def test_timeout_lanza_github_unavailable(fake_github):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("demasiado lento", request=request)

    fake_github(handler)

    with pytest.raises(github.GitHubUnavailable):
        await github.analyze_repository("encode", "httpx")


async def test_repositorio_sin_releases_devuelve_null(fake_github):
    """Un 404 en /releases/latest significa "no hay releases", no "no existe"."""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/releases/latest"):
            return httpx.Response(404, json={"message": "Not Found"})
        return successful_handler(request)

    fake_github(handler)

    result = await github.analyze_repository("octocat", "Hello-World")

    assert result.latest_release is None
    assert result.repository.name == REPO_PAYLOAD["name"]


async def test_repositorio_sin_commits_devuelve_lista_vacia(fake_github):
    """Un repositorio recien creado responde 409 Conflict en /commits."""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/commits"):
            return httpx.Response(409, json={"message": "Git Repository is empty."})
        return successful_handler(request)

    fake_github(handler)

    result = await github.analyze_repository("alguien", "repo-vacio")

    assert result.recent_commits == []


async def test_datos_ampliados_del_repositorio(fake_github):
    fake_github(successful_handler)

    repository = (await github.analyze_repository("encode", "httpx")).repository

    assert repository.license == "BSD-3-Clause"
    assert repository.topics == ["http", "asyncio"]
    assert repository.size_kb == 8594
    assert repository.is_archived is False


async def test_repositorio_sin_licencia_devuelve_null(fake_github):
    """GitHub manda license a null cuando el repositorio no declara ninguna."""

    def handler(request: httpx.Request) -> httpx.Response:
        if not is_repository_endpoint(request):
            return successful_handler(request)
        return httpx.Response(200, json={**REPO_PAYLOAD, "license": None})

    fake_github(handler)

    result = await github.analyze_repository("octocat", "Hello-World")

    assert result.repository.license is None


async def test_la_release_se_traduce_correctamente(fake_github):
    fake_github(successful_handler)

    release = (await github.analyze_repository("encode", "httpx")).latest_release

    assert release is not None
    assert release.tag == "0.28.1"
    assert release.name == "Version 0.28.1"


async def test_el_commit_se_traduce_correctamente(fake_github):
    fake_github(successful_handler)

    commit = (await github.analyze_repository("encode", "httpx")).recent_commits[0]

    assert commit.sha == "b5addb6", "el sha se recorta a 7 caracteres"
    assert commit.author == "musicinmybrain"
    assert commit.message == "Adapt test for chardet 6.0"


async def test_commit_sin_cuenta_de_github_usa_el_nombre_escrito(fake_github):
    """Si el correo del commit no esta asociado a una cuenta, author es null."""

    def handler(request: httpx.Request) -> httpx.Response:
        if not request.url.path.endswith("/commits"):
            return successful_handler(request)
        return httpx.Response(200, json=[{**COMMITS_PAYLOAD[0], "author": None}])

    fake_github(handler)

    commit = (await github.analyze_repository("encode", "httpx")).recent_commits[0]

    assert commit.author == "Ben Beasley"


async def test_del_mensaje_solo_se_guarda_la_primera_linea(fake_github):
    """Los mensajes largos llevan un cuerpo tras una linea en blanco."""

    def handler(request: httpx.Request) -> httpx.Response:
        if not request.url.path.endswith("/commits"):
            return successful_handler(request)
        original = COMMITS_PAYLOAD[0]
        commit = {
            **original,
            "commit": {
                **original["commit"],
                "message": "Titulo del commit\n\nExplicacion larga\nen varias lineas.",
            },
        }
        return httpx.Response(200, json=[commit])

    fake_github(handler)

    commit = (await github.analyze_repository("encode", "httpx")).recent_commits[0]

    assert commit.message == "Titulo del commit"
