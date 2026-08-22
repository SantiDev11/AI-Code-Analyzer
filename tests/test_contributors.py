"""Tests de Contributors Analysis.

El analisis hace una sola peticion a /contributors, asi que el payload de
cada manejador determina tanto `contributors` como `contributors_count`.
"""

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import github
from tests.conftest import successful_handler

VARIOS = [
    {
        "login": "ana",
        "contributions": 120,
        "avatar_url": "https://avatars.githubusercontent.com/u/1",
        "html_url": "https://github.com/ana",
    },
    {
        "login": "bruno",
        "contributions": 45,
        "avatar_url": "https://avatars.githubusercontent.com/u/2",
        "html_url": "https://github.com/bruno",
    },
    {
        "login": "carla",
        "contributions": 8,
        "avatar_url": "https://avatars.githubusercontent.com/u/3",
        "html_url": "https://github.com/carla",
    },
]


def responde_contributors(payload=None, status_code=200, headers=None):
    """Manejador que controla /contributors y deja el resto en normalidad."""

    def handler(request: httpx.Request) -> httpx.Response:
        if not request.url.path.endswith("/contributors"):
            return successful_handler(request)
        if payload is None:
            return httpx.Response(status_code, headers=headers or {})
        return httpx.Response(status_code, json=payload, headers=headers or {})

    return handler


async def test_repositorio_con_varios_contributors(fake_github):
    fake_github(responde_contributors(VARIOS))

    result = await github.analyze_repository("encode", "httpx")

    assert [person.username for person in result.contributors] == [
        "ana",
        "bruno",
        "carla",
    ]
    primero = result.contributors[0]
    assert primero.contributions == 120
    assert primero.avatar_url == "https://avatars.githubusercontent.com/u/1"
    assert primero.profile_url == "https://github.com/ana"


async def test_repositorio_con_un_solo_contributor(fake_github):
    fake_github(responde_contributors([VARIOS[0]]))

    result = await github.analyze_repository("SantiDev11", "AI-Code-Analyzer")

    assert len(result.contributors) == 1
    assert result.contributors[0].username == "ana"
    assert result.contributors_count == 1


async def test_respuesta_vacia_devuelve_lista_vacia(fake_github):
    fake_github(responde_contributors([]))

    result = await github.analyze_repository("alguien", "sin-contributors")

    assert result.contributors == []
    assert result.contributors_count == 0


async def test_repositorio_vacio_204_devuelve_lista_vacia(fake_github):
    """Sin commits, GitHub responde 204 No Content en vez de una lista."""
    fake_github(responde_contributors(status_code=204))

    result = await github.analyze_repository("alguien", "repo-vacio")

    assert result.contributors == []
    assert result.contributors_count == 0


async def test_repositorio_inexistente_lanza_not_found(fake_github):
    fake_github(lambda request: httpx.Response(404, json={"message": "Not Found"}))

    with pytest.raises(github.RepositoryNotFound):
        await github.analyze_repository("SantiDev11", "no-existe")


async def test_error_de_la_api_de_github_lanza_github_error(fake_github):
    fake_github(responde_contributors(payload={"message": "boom"}, status_code=500))

    with pytest.raises(github.GitHubError):
        await github.analyze_repository("encode", "httpx")


async def test_respuesta_inesperada_de_github_lanza_github_error(fake_github):
    """Faltan campos en un contribuidor que si tiene usuario: 502, no error 500.

    Distinto de no tener login, que es un caso previsto y se omite en silencio.
    """
    fake_github(responde_contributors([{"login": "ana", "contributions": 3}]))

    with pytest.raises(github.GitHubError):
        await github.analyze_repository("encode", "httpx")


async def test_los_contributors_se_ordenan_de_mayor_a_menor(fake_github):
    """No damos por hecho el orden de GitHub: lo garantizamos nosotros."""
    desordenados = [VARIOS[2], VARIOS[0], VARIOS[1]]
    fake_github(responde_contributors(desordenados))

    result = await github.analyze_repository("encode", "httpx")

    contribuciones = [person.contributions for person in result.contributors]
    assert contribuciones == [120, 45, 8]
    assert contribuciones == sorted(contribuciones, reverse=True)


async def test_contributors_count_coincide_con_lo_devuelto(fake_github):
    """El contador describe la lista que publicamos, no el repositorio entero."""
    fake_github(responde_contributors(VARIOS))

    result = await github.analyze_repository("encode", "httpx")

    assert result.contributors_count == 3
    assert result.contributors_count == len(result.contributors)


async def test_contributor_sin_login_se_omite(fake_github):
    """Un contribuidor anonimo no tiene usuario, avatar ni perfil.

    Se descarta esa entrada, pero el resto de la lista sigue siendo valida:
    una sola entrada incompleta no debe tumbar el analisis entero.
    """
    anonimo = {"login": None, "contributions": 999, "type": "Anonymous"}
    fake_github(responde_contributors([anonimo, VARIOS[0], VARIOS[1]]))

    result = await github.analyze_repository("encode", "httpx")

    assert [person.username for person in result.contributors] == ["ana", "bruno"]
    assert result.contributors_count == 2, "el descartado no cuenta"


async def test_contributor_sin_la_clave_login_se_omite(fake_github):
    """Variante: la clave no viene vacia, viene directamente ausente."""
    fake_github(responde_contributors([{"contributions": 999}, VARIOS[0]]))

    result = await github.analyze_repository("encode", "httpx")

    assert [person.username for person in result.contributors] == ["ana"]
    assert result.contributors_count == 1


async def test_no_se_exponen_campos_innecesarios_de_github(fake_github):
    """GitHub manda una veintena de campos; nosotros publicamos cuatro."""
    crudo = {
        **VARIOS[0],
        "node_id": "MDQ6VXNlcjE=",
        "gravatar_id": "",
        "url": "https://api.github.com/users/ana",
        "followers_url": "https://api.github.com/users/ana/followers",
        "type": "User",
        "site_admin": False,
    }
    fake_github(responde_contributors([crudo]))

    result = await github.analyze_repository("encode", "httpx")

    assert set(result.contributors[0].model_dump()) == {
        "username",
        "contributions",
        "avatar_url",
        "profile_url",
    }


def test_integracion_con_el_endpoint_analyze(fake_github):
    """Recorrido completo por HTTP: ruta, servicio, modelo y serializacion."""
    fake_github(responde_contributors(VARIOS))

    response = TestClient(app).get("/analyze/encode/httpx")

    assert response.status_code == 200
    body = response.json()
    assert body["contributors_count"] == 3
    assert body["contributors"] == [
        {
            "username": "ana",
            "contributions": 120,
            "avatar_url": "https://avatars.githubusercontent.com/u/1",
            "profile_url": "https://github.com/ana",
        },
        {
            "username": "bruno",
            "contributions": 45,
            "avatar_url": "https://avatars.githubusercontent.com/u/2",
            "profile_url": "https://github.com/bruno",
        },
        {
            "username": "carla",
            "contributions": 8,
            "avatar_url": "https://avatars.githubusercontent.com/u/3",
            "profile_url": "https://github.com/carla",
        },
    ]


def test_integracion_repositorio_inexistente_devuelve_404(fake_github):
    fake_github(lambda request: httpx.Response(404, json={"message": "Not Found"}))

    response = TestClient(app).get("/analyze/SantiDev11/no-existe")

    assert response.status_code == 404
