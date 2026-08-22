"""Utilidades compartidas por los tests.

Ningun test toca la red: sustituimos el cliente HTTP real por uno que devuelve
respuestas simuladas. Asi los tests son instantaneos, funcionan sin internet y
no consumen la cuota de la GitHub API.
"""

from collections.abc import Callable

import httpx
import pytest

from app.services import github

# Respuesta tipica de GET /repos/{owner}/{repo}, recortada a lo que usamos.
REPO_PAYLOAD = {
    "name": "httpx",
    "full_name": "encode/httpx",
    "description": "A next generation HTTP client for Python.",
    "stargazers_count": 15429,
    "forks_count": 1256,
    "open_issues_count": 143,
    "created_at": "2019-04-04T12:27:00Z",
    "updated_at": "2024-05-02T08:12:44Z",
    "language": "Python",
    "html_url": "https://github.com/encode/httpx",
    "license": {"spdx_id": "BSD-3-Clause"},
    "topics": ["http", "asyncio"],
    "size": 8594,
    "archived": False,
}

LANGUAGES_PAYLOAD = {"Python": 570031, "Shell": 2821}

RELEASE_PAYLOAD = {
    "tag_name": "0.28.1",
    "name": "Version 0.28.1",
    "published_at": "2024-12-06T15:36:24Z",
    "html_url": "https://github.com/encode/httpx/releases/tag/0.28.1",
}

COMMITS_PAYLOAD = [
    {
        "sha": "b5addb64f0161ff6bfe94c124ef76f6a1fba5254",
        "html_url": "https://github.com/encode/httpx/commit/b5addb6",
        "author": {"login": "musicinmybrain"},
        "commit": {
            "message": "Adapt test for chardet 6.0",
            "author": {"name": "Ben Beasley", "date": "2026-02-23T10:40:42Z"},
        },
    }
]

# Respuesta de GET /contributors, recortada a los campos que usamos.
CONTRIBUTORS_PAYLOAD = [
    {
        "login": "tomchristie",
        "contributions": 1042,
        "avatar_url": "https://avatars.githubusercontent.com/u/647359",
        "html_url": "https://github.com/tomchristie",
    },
    {
        "login": "florimondmanca",
        "contributions": 318,
        "avatar_url": "https://avatars.githubusercontent.com/u/15911462",
        "html_url": "https://github.com/florimondmanca",
    },
]


@pytest.fixture(autouse=True)
def clean_cache():
    """Vacia la cache antes de cada test.

    La cache es estado global del modulo: sin esto, un test dejaria datos
    guardados que el siguiente encontraria, y el resultado dependeria del
    orden de ejecucion.
    """
    github._cache.clear()
    yield
    github._cache.clear()


@pytest.fixture
def fake_github(monkeypatch) -> Callable[[Callable], None]:
    """Instala un GitHub simulado.

    Devuelve una funcion a la que se le pasa un manejador: recibe la peticion
    y decide que respuesta devolver segun la ruta.
    """

    def install(handler: Callable[[httpx.Request], httpx.Response]) -> None:
        def create_client() -> httpx.AsyncClient:
            return httpx.AsyncClient(
                base_url=github.API_BASE, transport=httpx.MockTransport(handler)
            )

        monkeypatch.setattr(github, "_create_client", create_client)

    return install


def is_repository_endpoint(request: httpx.Request) -> bool:
    """True solo para /repos/{owner}/{repo}, no para sus sub-recursos.

    Util en los tests que quieren cambiar los datos del repositorio y dejar
    que el resto de endpoints respondan con normalidad.
    """
    return len(request.url.path.strip("/").split("/")) == 3


def successful_handler(request: httpx.Request) -> httpx.Response:
    """Simula un repositorio que existe y responde correctamente a todo."""
    path = request.url.path

    if path.endswith("/releases/latest"):
        return httpx.Response(200, json=RELEASE_PAYLOAD)

    if path.endswith("/commits"):
        return httpx.Response(200, json=COMMITS_PAYLOAD)

    if path.endswith("/languages"):
        return httpx.Response(200, json=LANGUAGES_PAYLOAD)

    if path.endswith("/contributors"):
        return httpx.Response(200, json=CONTRIBUTORS_PAYLOAD)

    return httpx.Response(200, json=REPO_PAYLOAD)
