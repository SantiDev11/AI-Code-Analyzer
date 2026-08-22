"""Tests de la capa de servicio: traduccion de datos y manejo de errores."""

import httpx
import pytest

from app.services import github
from tests.conftest import (
    CONTRIBUTORS_LINK_HEADER,
    LANGUAGES_PAYLOAD,
    REPO_PAYLOAD,
    successful_handler,
)


async def test_analiza_repositorio_correctamente(fake_github):
    """El caso feliz: los tres endpoints responden y se combinan bien."""
    fake_github(successful_handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.repository.name == REPO_PAYLOAD["name"]
    assert result.repository.stars == REPO_PAYLOAD["stargazers_count"]
    assert result.repository.forks == REPO_PAYLOAD["forks_count"]
    assert result.repository.open_issues == REPO_PAYLOAD["open_issues_count"]
    assert result.repository.primary_language == REPO_PAYLOAD["language"]
    assert result.repository.url == REPO_PAYLOAD["html_url"]
    assert result.languages == LANGUAGES_PAYLOAD
    # El total sale del rel="last" de la cabecera Link, no de contar elementos.
    assert result.contributors_count == 247


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


async def test_lista_de_contributors_demasiado_grande_devuelve_null(fake_github):
    """Un 403 por historial enorme NO es falta de cuota: devolvemos null."""

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

    assert result.contributors_count is None
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
        if request.url.path.endswith(("/languages", "/contributors")):
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


@pytest.mark.parametrize(
    ("link_header", "expected"),
    [
        (CONTRIBUTORS_LINK_HEADER, 247),
        ("", None),
        ('<https://api.github.com/x?page=2>; rel="next"', None),
        ('<https://api.github.com/x?per_page=1&page=9>; rel="last"', 9),
    ],
)
def test_extraccion_de_la_ultima_pagina(link_header, expected):
    """Funcion pura: no necesita simular nada."""
    assert github._extract_last_page(link_header) == expected
