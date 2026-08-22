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
    "description": "A next generation HTTP client for Python.",
    "stargazers_count": 15429,
    "forks_count": 1256,
    "open_issues_count": 143,
    "created_at": "2019-04-04T12:27:00Z",
    "updated_at": "2024-05-02T08:12:44Z",
    "language": "Python",
    "html_url": "https://github.com/encode/httpx",
}

LANGUAGES_PAYLOAD = {"Python": 570031, "Shell": 2821}

CONTRIBUTORS_LINK_HEADER = (
    '<https://api.github.com/repositories/1/contributors?per_page=1&page=2>; rel="next", '
    '<https://api.github.com/repositories/1/contributors?per_page=1&page=247>; rel="last"'
)


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


def successful_handler(request: httpx.Request) -> httpx.Response:
    """Simula un repositorio que existe y responde correctamente a todo."""
    path = request.url.path

    if path.endswith("/languages"):
        return httpx.Response(200, json=LANGUAGES_PAYLOAD)

    if path.endswith("/contributors"):
        return httpx.Response(
            200, json=[{"login": "alguien"}], headers={"Link": CONTRIBUTORS_LINK_HEADER}
        )

    return httpx.Response(200, json=REPO_PAYLOAD)
