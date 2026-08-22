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
    "default_branch": "master",
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

# Respuesta de GET /issues. GitHub mezcla issues y pull requests: el tercer
# elemento lleva la clave "pull_request" y por tanto NO es un issue.
ISSUES_PAYLOAD = [
    {
        "number": 15,
        "title": "Improve error handling",
        "state": "open",
        "user": {"login": "SantiDev11"},
        "created_at": "2026-08-22T10:30:00Z",
        "updated_at": "2026-08-22T12:00:00Z",
        "html_url": "https://github.com/encode/httpx/issues/15",
    },
    {
        "number": 12,
        "title": "Timeout mal documentado",
        "state": "closed",
        "user": {"login": "tomchristie"},
        "created_at": "2026-07-01T08:00:00Z",
        "updated_at": "2026-07-05T11:20:00Z",
        "html_url": "https://github.com/encode/httpx/issues/12",
    },
    {
        "number": 11,
        "title": "Bump actions/setup-python",
        "state": "open",
        "user": {"login": "dependabot[bot]"},
        "created_at": "2026-06-30T07:00:00Z",
        "updated_at": "2026-06-30T07:00:00Z",
        "html_url": "https://github.com/encode/httpx/pull/11",
        "pull_request": {"url": "https://api.github.com/.../pulls/11"},
    },
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


# Respuesta de GET /pulls. El segundo esta cerrado y mergeado (merged_at con
# fecha) y el tercero cerrado sin mergear (merged_at null): en el listado de
# GitHub esa fecha es el unico dato que distingue un caso del otro.
PULLS_PAYLOAD = [
    {
        "number": 42,
        "title": "Add issue analysis",
        "state": "open",
        "user": {"login": "SantiDev11"},
        "created_at": "2026-08-22T09:00:00Z",
        "updated_at": "2026-08-22T11:00:00Z",
        "closed_at": None,
        "merged_at": None,
        "head": {"ref": "feat/issues"},
        "base": {"ref": "main"},
        "html_url": "https://github.com/encode/httpx/pull/42",
    },
    {
        "number": 40,
        "title": "Fix timeout handling",
        "state": "closed",
        "user": {"login": "tomchristie"},
        "created_at": "2026-08-20T10:00:00Z",
        "updated_at": "2026-08-21T10:00:00Z",
        "closed_at": "2026-08-21T09:30:00Z",
        "merged_at": "2026-08-21T09:30:00Z",
        "head": {"ref": "fix/timeout"},
        "base": {"ref": "main"},
        "html_url": "https://github.com/encode/httpx/pull/40",
    },
    {
        "number": 38,
        "title": "Experimento descartado",
        "state": "closed",
        "user": {"login": "florimondmanca"},
        "created_at": "2026-08-18T08:00:00Z",
        "updated_at": "2026-08-19T08:00:00Z",
        "closed_at": "2026-08-19T08:00:00Z",
        "merged_at": None,
        "head": {"ref": "spike/idea"},
        "base": {"ref": "main"},
        "html_url": "https://github.com/encode/httpx/pull/38",
    },
]


# Respuesta de GET /releases, con los tres casos que hay que distinguir: uno
# publicado y estable, uno publicado pero marcado como version previa, y un
# borrador que nunca se publico y por eso tiene published_at en null.
RELEASES_PAYLOAD = [
    {
        "id": 300,
        "tag_name": "0.28.1",
        "name": "Version 0.28.1",
        "body": "Correcciones menores.",
        "draft": False,
        "prerelease": False,
        "created_at": "2024-12-06T15:00:00Z",
        "published_at": "2024-12-06T15:36:24Z",
        "author": {"login": "tomchristie"},
        "html_url": "https://github.com/encode/httpx/releases/tag/0.28.1",
    },
    {
        "id": 290,
        "tag_name": "0.29.0rc1",
        "name": "Version 0.29.0 rc1",
        "body": None,
        "draft": False,
        "prerelease": True,
        "created_at": "2024-11-20T09:00:00Z",
        "published_at": "2024-11-20T09:30:00Z",
        "author": {"login": "florimondmanca"},
        "html_url": "https://github.com/encode/httpx/releases/tag/0.29.0rc1",
    },
    {
        "id": 280,
        "tag_name": "0.30.0",
        "name": None,
        "body": None,
        "draft": True,
        "prerelease": False,
        "created_at": "2024-11-01T08:00:00Z",
        "published_at": None,
        "author": {"login": "SantiDev11"},
        "html_url": "https://github.com/encode/httpx/releases/tag/0.30.0",
    },
]


# Respuesta de GET /git/trees/{branch}?recursive=1
TREE_PAYLOAD = {
    "sha": "c5b97d5ae6c19d5c5df71a34c7fbeeda2479ccbc",
    "url": "https://api.github.com/repos/encode/httpx/git/trees/master",
    "tree": [
        {"path": "README.md", "mode": "100644", "type": "blob", "sha": "123"},
        {"path": "CONTRIBUTING.md", "mode": "100644", "type": "blob", "sha": "124"},
        {"path": "tests/test_client.py", "mode": "100644", "type": "blob", "sha": "456"},
        {"path": ".github/workflows/test.yml", "mode": "100644", "type": "blob", "sha": "789"},
        {"path": ".flake8", "mode": "100644", "type": "blob", "sha": "790"},
        {"path": ".editorconfig", "mode": "100644", "type": "blob", "sha": "791"},
        {"path": "pyproject.toml", "mode": "100644", "type": "blob", "sha": "792"},
        {"path": ".coveragerc", "mode": "100644", "type": "blob", "sha": "793"},
    ],
    "truncated": False,
}


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

    if path.endswith("/releases"):
        return httpx.Response(200, json=RELEASES_PAYLOAD)

    if path.endswith("/commits"):
        return httpx.Response(200, json=COMMITS_PAYLOAD)

    if path.endswith("/issues"):
        return httpx.Response(200, json=ISSUES_PAYLOAD)

    if path.endswith("/pulls"):
        return httpx.Response(200, json=PULLS_PAYLOAD)

    if path.endswith("/languages"):
        return httpx.Response(200, json=LANGUAGES_PAYLOAD)

    if path.endswith("/contributors"):
        return httpx.Response(200, json=CONTRIBUTORS_PAYLOAD)

    if "/git/trees/" in path:
        return httpx.Response(200, json=TREE_PAYLOAD)

    return httpx.Response(200, json=REPO_PAYLOAD)
