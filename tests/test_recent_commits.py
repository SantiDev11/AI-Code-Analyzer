"""Tests de Recent Commits Analysis.

Los manejadores de aqui controlan /commits y dejan que el resto de endpoints
respondan con normalidad, asi que el payload determina `recent_commits`.
"""

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import github
from tests.conftest import successful_handler


def commit_crudo(sha, mensaje, login, nombre, fecha):
    """Construye un commit con la forma que devuelve GitHub."""
    return {
        "sha": sha,
        "html_url": f"https://github.com/encode/httpx/commit/{sha}",
        "author": {"login": login} if login else None,
        "commit": {
            "message": mensaje,
            "author": {"name": nombre, "date": fecha},
        },
    }


VARIOS = [
    commit_crudo(
        "aaaaaaa1111111111111111111111111111111111",
        "feat: add contributor analysis",
        "SantiDev11",
        "Kevin Pedraza",
        "2026-08-22T10:30:00Z",
    ),
    commit_crudo(
        "bbbbbbb2222222222222222222222222222222222",
        "fix: corregir la ruta de la hoja de estilos",
        "chantycampox",
        "Chanty Campo",
        "2026-08-21T09:15:00Z",
    ),
    commit_crudo(
        "ccccccc3333333333333333333333333333333333",
        "docs: actualizar el README",
        None,
        "Alguien Sin Cuenta",
        "2026-08-20T18:00:00Z",
    ),
]


def responde_commits(payload=None, status_code=200):
    """Manejador que controla /commits y anota los parametros pedidos."""
    parametros = []

    def handler(request: httpx.Request) -> httpx.Response:
        if not request.url.path.endswith("/commits"):
            return successful_handler(request)
        parametros.append(dict(request.url.params))
        if payload is None:
            return httpx.Response(status_code)
        return httpx.Response(status_code, json=payload)

    return handler, parametros


# --------------------------------------------------------------------------
# Casos correctos
# --------------------------------------------------------------------------


async def test_repositorio_con_varios_commits(fake_github):
    handler, _ = responde_commits(VARIOS)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert len(result.recent_commits) == 3
    primero = result.recent_commits[0]
    assert primero.sha == "aaaaaaa", "el sha se recorta a 7 caracteres"
    assert primero.message == "feat: add contributor analysis"
    assert primero.author == "SantiDev11"


async def test_repositorio_con_un_solo_commit(fake_github):
    handler, _ = responde_commits([VARIOS[0]])
    fake_github(handler)

    result = await github.analyze_repository("SantiDev11", "AI-Code-Analyzer")

    assert len(result.recent_commits) == 1
    assert result.recent_commits[0].author == "SantiDev11"


async def test_respuesta_vacia_devuelve_lista_vacia(fake_github):
    handler, _ = responde_commits([])
    fake_github(handler)

    result = await github.analyze_repository("alguien", "sin-commits")

    assert result.recent_commits == []


async def test_repositorio_vacio_409_devuelve_lista_vacia(fake_github):
    """Un repositorio recien creado responde 409 Conflict en /commits."""
    handler, _ = responde_commits(payload={"message": "empty"}, status_code=409)
    fake_github(handler)

    result = await github.analyze_repository("alguien", "repo-vacio")

    assert result.recent_commits == []


# --------------------------------------------------------------------------
# Datos incompletos
# --------------------------------------------------------------------------


async def test_commit_sin_cuenta_de_github_usa_el_nombre_firmado(fake_github):
    """author es null cuando el correo no esta asociado a ninguna cuenta."""
    handler, _ = responde_commits([VARIOS[2]])
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.recent_commits[0].author == "Alguien Sin Cuenta"


async def test_commit_sin_cuenta_ni_nombre_deja_el_autor_en_null(fake_github):
    """Sin cuenta y sin nombre firmado no hay autor: null, no un invento."""
    sin_autor = commit_crudo("ddd", "chore: algo", None, None, "2026-08-22T10:00:00Z")
    sin_autor["commit"]["author"] = {"date": "2026-08-22T10:00:00Z"}
    handler, _ = responde_commits([sin_autor])
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.recent_commits[0].author is None


async def test_commit_sin_fecha_lanza_github_error(fake_github):
    """La fecha no tiene sustituto razonable: error controlado, no un 500."""
    sin_fecha = commit_crudo("eee", "chore: algo", "ana", "Ana", "2026-01-01T00:00:00Z")
    del sin_fecha["commit"]["author"]["date"]
    handler, _ = responde_commits([sin_fecha])
    fake_github(handler)

    with pytest.raises(github.GitHubError):
        await github.analyze_repository("encode", "httpx")


async def test_respuesta_inesperada_lanza_github_error(fake_github):
    """Una lista sin la forma que esperamos no debe reventar el servidor."""
    handler, _ = responde_commits([{"algo": "distinto"}])
    fake_github(handler)

    with pytest.raises(github.GitHubError):
        await github.analyze_repository("encode", "httpx")


async def test_del_mensaje_solo_se_guarda_la_primera_linea(fake_github):
    largo = commit_crudo(
        "fff",
        "Titulo\n\nCuerpo largo\nen varias lineas.",
        "ana",
        "Ana",
        "2026-01-01T00:00:00Z",
    )
    handler, _ = responde_commits([largo])
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.recent_commits[0].message == "Titulo"


# --------------------------------------------------------------------------
# Errores de GitHub
# --------------------------------------------------------------------------


async def test_repositorio_inexistente_lanza_not_found(fake_github):
    fake_github(lambda request: httpx.Response(404, json={"message": "Not Found"}))

    with pytest.raises(github.RepositoryNotFound):
        await github.analyze_repository("SantiDev11", "no-existe")


async def test_error_de_la_api_de_github_lanza_github_error(fake_github):
    handler, _ = responde_commits(payload={"message": "boom"}, status_code=500)
    fake_github(handler)

    with pytest.raises(github.GitHubError):
        await github.analyze_repository("encode", "httpx")


# --------------------------------------------------------------------------
# Modelo y limite
# --------------------------------------------------------------------------


async def test_solo_se_devuelven_los_campos_de_nuestro_modelo(fake_github):
    """GitHub manda decenas de campos por commit; publicamos cinco."""
    crudo = {
        **VARIOS[0],
        "node_id": "C_kwDO",
        "comments_url": "https://api.github.com/algo",
        "parents": [{"sha": "otro"}],
        "committer": {"login": "web-flow"},
    }
    handler, _ = responde_commits([crudo])
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert set(result.recent_commits[0].model_dump()) == {
        "sha",
        "message",
        "author",
        "date",
        "url",
    }


async def test_por_defecto_se_piden_diez_commits(fake_github):
    handler, parametros = responde_commits(VARIOS)
    fake_github(handler)

    await github.analyze_repository("encode", "httpx")

    assert parametros[0]["per_page"] == "10"


async def test_el_limite_pedido_llega_a_github(fake_github):
    handler, parametros = responde_commits(VARIOS)
    fake_github(handler)

    await github.analyze_repository("encode", "httpx", commits_limit=25)

    assert parametros[0]["per_page"] == "25"


async def test_limites_distintos_no_comparten_cache(fake_github):
    """Pedir 30 tras pedir 10 debe volver a consultar, no reutilizar la corta."""
    handler, parametros = responde_commits(VARIOS)
    fake_github(handler)

    await github.analyze_repository("encode", "httpx", commits_limit=10)
    await github.analyze_repository("encode", "httpx", commits_limit=30)

    assert [p["per_page"] for p in parametros] == ["10", "30"]


# --------------------------------------------------------------------------
# Integracion por HTTP
# --------------------------------------------------------------------------


def test_integracion_con_el_endpoint_analyze(fake_github):
    handler, _ = responde_commits(VARIOS)
    fake_github(handler)

    response = TestClient(app).get("/analyze/encode/httpx")

    assert response.status_code == 200
    commits = response.json()["recent_commits"]
    assert len(commits) == 3
    assert commits[0] == {
        "sha": "aaaaaaa",
        "message": "feat: add contributor analysis",
        "author": "SantiDev11",
        "date": "2026-08-22T10:30:00Z",
        "url": (
            "https://github.com/encode/httpx/commit/"
            "aaaaaaa1111111111111111111111111111111111"
        ),
    }


def test_integracion_el_parametro_commits_llega_a_github(fake_github):
    handler, parametros = responde_commits(VARIOS)
    fake_github(handler)

    response = TestClient(app).get("/analyze/encode/httpx?commits=3")

    assert response.status_code == 200
    assert parametros[0]["per_page"] == "3"


@pytest.mark.parametrize("valor", [0, -1, 101, 5000])
def test_integracion_cantidades_fuera_de_rango_devuelven_422(fake_github, valor):
    """No se permiten cantidades absurdas: FastAPI las rechaza antes de GitHub."""
    handler, parametros = responde_commits(VARIOS)
    fake_github(handler)

    response = TestClient(app).get(f"/analyze/encode/httpx?commits={valor}")

    assert response.status_code == 422
    assert parametros == [], "no se llega a consultar GitHub"
