"""Tests de Issues Analysis.

GitHub sirve issues y pull requests por el mismo endpoint. Estos tests
comprueban sobre todo que los pull requests nunca se cuelan como issues.
"""

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import github
from tests.conftest import successful_handler


def issue_crudo(number, title, state, login, creado="2026-08-22T10:30:00Z"):
    """Construye un issue con la forma que devuelve GitHub."""
    return {
        "number": number,
        "title": title,
        "state": state,
        "user": {"login": login} if login else None,
        "created_at": creado,
        "updated_at": "2026-08-22T12:00:00Z",
        "html_url": f"https://github.com/encode/httpx/issues/{number}",
    }


def pull_request_crudo(number, title, state="open"):
    """Un pull request tal y como lo sirve /issues: con clave pull_request."""
    return {
        **issue_crudo(number, title, state, "dependabot[bot]"),
        "html_url": f"https://github.com/encode/httpx/pull/{number}",
        "pull_request": {"url": f"https://api.github.com/repos/x/y/pulls/{number}"},
    }


ABIERTOS_Y_CERRADOS = [
    issue_crudo(15, "Improve error handling", "open", "SantiDev11"),
    issue_crudo(14, "Documentar el timeout", "open", "tomchristie"),
    issue_crudo(12, "Fallo al parsear cookies", "closed", "florimondmanca"),
]


def responde_issues(payload=None, status_code=200):
    """Manejador que controla /issues y anota los parametros pedidos."""
    parametros = []

    def handler(request: httpx.Request) -> httpx.Response:
        if not request.url.path.endswith("/issues"):
            return successful_handler(request)
        parametros.append(dict(request.url.params))
        if payload is None:
            return httpx.Response(status_code)
        return httpx.Response(status_code, json=payload)

    return handler, parametros


# --------------------------------------------------------------------------
# Casos correctos
# --------------------------------------------------------------------------


async def test_repositorio_con_varios_issues(fake_github):
    handler, _ = responde_issues(ABIERTOS_Y_CERRADOS)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert [issue.number for issue in result.issues] == [15, 14, 12]
    primero = result.issues[0]
    assert primero.title == "Improve error handling"
    assert primero.state == "open"
    assert primero.author == "SantiDev11"
    assert primero.url == "https://github.com/encode/httpx/issues/15"


async def test_issues_abiertos_y_cerrados_se_clasifican_bien(fake_github):
    handler, _ = responde_issues(ABIERTOS_Y_CERRADOS)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert [issue.state for issue in result.issues] == ["open", "open", "closed"]


async def test_se_piden_los_cerrados_tambien(fake_github):
    """Sin state=all GitHub devuelve solo los abiertos y no habria cerrados."""
    handler, parametros = responde_issues(ABIERTOS_Y_CERRADOS)
    fake_github(handler)

    await github.analyze_repository("encode", "httpx")

    assert parametros[0]["state"] == "all"


async def test_repositorio_sin_issues_devuelve_lista_vacia(fake_github):
    handler, _ = responde_issues([])
    fake_github(handler)

    result = await github.analyze_repository("alguien", "sin-issues")

    assert result.issues == []
    assert result.issues_count == 0
    assert result.open_issues_count == 0
    assert result.closed_issues_count == 0


async def test_issues_desactivados_no_es_un_error(fake_github):
    """GitHub responde 404 en /issues si el repositorio los tiene apagados.

    El repositorio existe, asi que la respuesta correcta es la lista vacia.
    """
    handler, _ = responde_issues(payload={"message": "Not Found"}, status_code=404)
    fake_github(handler)

    result = await github.analyze_repository("alguien", "sin-issues-activados")

    assert result.issues == []
    assert result.repository.name == "httpx"


# --------------------------------------------------------------------------
# Pull requests
# --------------------------------------------------------------------------


async def test_los_pull_requests_no_se_cuentan_como_issues(fake_github):
    """El caso central: /issues mezcla ambos y solo queremos issues."""
    mezcla = [
        ABIERTOS_Y_CERRADOS[0],
        pull_request_crudo(99, "Bump actions/setup-python"),
        ABIERTOS_Y_CERRADOS[2],
        pull_request_crudo(98, "Bump httpx", state="closed"),
    ]
    handler, _ = responde_issues(mezcla)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert [issue.number for issue in result.issues] == [15, 12]
    assert 99 not in [issue.number for issue in result.issues]
    assert result.issues_count == 2, "los dos pull requests quedan fuera"
    assert result.open_issues_count == 1
    assert result.closed_issues_count == 1


async def test_una_respuesta_de_solo_pull_requests_da_cero_issues(fake_github):
    handler, _ = responde_issues([pull_request_crudo(99, "a"), pull_request_crudo(98, "b")])
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.issues == []
    assert result.issues_count == 0


# --------------------------------------------------------------------------
# Contadores
# --------------------------------------------------------------------------


async def test_issues_count_es_la_longitud_de_la_lista(fake_github):
    handler, _ = responde_issues(ABIERTOS_Y_CERRADOS)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.issues_count == 3
    assert result.issues_count == len(result.issues)


async def test_open_issues_count(fake_github):
    handler, _ = responde_issues(ABIERTOS_Y_CERRADOS)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.open_issues_count == 2


async def test_closed_issues_count(fake_github):
    handler, _ = responde_issues(ABIERTOS_Y_CERRADOS)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.closed_issues_count == 1


async def test_abiertos_mas_cerrados_suman_el_total(fake_github):
    """La invariante que pediste, comprobada tambien con pull requests dentro."""
    mezcla = [*ABIERTOS_Y_CERRADOS, pull_request_crudo(99, "un PR")]
    handler, _ = responde_issues(mezcla)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.open_issues_count + result.closed_issues_count == result.issues_count


# --------------------------------------------------------------------------
# Datos incompletos y errores
# --------------------------------------------------------------------------


async def test_issue_sin_author_deja_el_campo_en_null(fake_github):
    """GitHub manda user null cuando la cuenta que lo abrio fue borrada."""
    handler, _ = responde_issues([issue_crudo(15, "Huerfano", "open", None)])
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.issues[0].author is None
    assert result.issues_count == 1, "sigue siendo un issue valido"


async def test_repositorio_inexistente_lanza_not_found(fake_github):
    fake_github(lambda request: httpx.Response(404, json={"message": "Not Found"}))

    with pytest.raises(github.RepositoryNotFound):
        await github.analyze_repository("SantiDev11", "no-existe")


async def test_error_de_la_api_de_github_lanza_github_error(fake_github):
    handler, _ = responde_issues(payload={"message": "boom"}, status_code=500)
    fake_github(handler)

    with pytest.raises(github.GitHubError):
        await github.analyze_repository("encode", "httpx")


async def test_respuesta_inesperada_lanza_github_error(fake_github):
    """Una lista sin la forma que esperamos no debe reventar el servidor."""
    handler, _ = responde_issues([{"algo": "distinto"}])
    fake_github(handler)

    with pytest.raises(github.GitHubError):
        await github.analyze_repository("encode", "httpx")


async def test_estado_desconocido_lanza_github_error(fake_github):
    """El modelo solo admite open o closed: cualquier otra cosa es sospechosa."""
    raro = {**issue_crudo(15, "Raro", "open", "ana"), "state": "merged"}
    handler, _ = responde_issues([raro])
    fake_github(handler)

    with pytest.raises(github.GitHubError):
        await github.analyze_repository("encode", "httpx")


# --------------------------------------------------------------------------
# Modelo y limite
# --------------------------------------------------------------------------


async def test_solo_se_devuelven_los_campos_de_nuestro_modelo(fake_github):
    """GitHub manda decenas de campos por issue; publicamos siete."""
    crudo = {
        **ABIERTOS_Y_CERRADOS[0],
        "node_id": "I_kwDO",
        "labels": [{"name": "bug"}],
        "assignees": [],
        "body": "Un cuerpo larguisimo que no queremos publicar",
        "comments": 4,
        "author_association": "OWNER",
    }
    handler, _ = responde_issues([crudo])
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert set(result.issues[0].model_dump()) == {
        "number",
        "title",
        "state",
        "author",
        "created_at",
        "updated_at",
        "url",
    }


async def test_por_defecto_se_piden_diez_issues(fake_github):
    handler, parametros = responde_issues(ABIERTOS_Y_CERRADOS)
    fake_github(handler)

    await github.analyze_repository("encode", "httpx")

    assert parametros[0]["per_page"] == "10"


async def test_el_limite_pedido_llega_a_github(fake_github):
    handler, parametros = responde_issues(ABIERTOS_Y_CERRADOS)
    fake_github(handler)

    await github.analyze_repository("encode", "httpx", issues_limit=40)

    assert parametros[0]["per_page"] == "40"


async def test_limites_distintos_no_comparten_cache(fake_github):
    handler, parametros = responde_issues(ABIERTOS_Y_CERRADOS)
    fake_github(handler)

    await github.analyze_repository("encode", "httpx", issues_limit=10)
    await github.analyze_repository("encode", "httpx", issues_limit=40)

    assert [p["per_page"] for p in parametros] == ["10", "40"]


async def test_el_limite_de_commits_sigue_funcionando(fake_github):
    """La clave de cache cambio: hay que comprobar que no rompio lo anterior."""
    handler, _ = responde_issues(ABIERTOS_Y_CERRADOS)
    fake_github(handler)

    primero = await github.analyze_repository("encode", "httpx", commits_limit=5)
    segundo = await github.analyze_repository("encode", "httpx", commits_limit=5)

    assert primero.cached is False
    assert segundo.cached is True, "mismos limites, misma entrada de cache"


# --------------------------------------------------------------------------
# Integracion por HTTP
# --------------------------------------------------------------------------


def test_integracion_con_el_endpoint_analyze(fake_github):
    handler, _ = responde_issues([*ABIERTOS_Y_CERRADOS, pull_request_crudo(99, "PR")])
    fake_github(handler)

    response = TestClient(app).get("/analyze/encode/httpx")

    assert response.status_code == 200
    body = response.json()
    assert body["issues_count"] == 3
    assert body["open_issues_count"] == 2
    assert body["closed_issues_count"] == 1
    assert body["issues"][0] == {
        "number": 15,
        "title": "Improve error handling",
        "state": "open",
        "author": "SantiDev11",
        "created_at": "2026-08-22T10:30:00Z",
        "updated_at": "2026-08-22T12:00:00Z",
        "url": "https://github.com/encode/httpx/issues/15",
    }


def test_integracion_el_parametro_issues_llega_a_github(fake_github):
    handler, parametros = responde_issues(ABIERTOS_Y_CERRADOS)
    fake_github(handler)

    response = TestClient(app).get("/analyze/encode/httpx?issues=3")

    assert response.status_code == 200
    assert parametros[0]["per_page"] == "3"


@pytest.mark.parametrize("valor", [0, -1, 101, 5000])
def test_integracion_cantidades_fuera_de_rango_devuelven_422(fake_github, valor):
    handler, parametros = responde_issues(ABIERTOS_Y_CERRADOS)
    fake_github(handler)

    response = TestClient(app).get(f"/analyze/encode/httpx?issues={valor}")

    assert response.status_code == 422
    assert parametros == [], "no se llega a consultar GitHub"


def test_integracion_las_funcionalidades_anteriores_siguen_ahi(fake_github):
    """Issues no debe haber desplazado nada de lo que ya devolviamos."""
    handler, _ = responde_issues(ABIERTOS_Y_CERRADOS)
    fake_github(handler)

    body = TestClient(app).get("/analyze/encode/httpx").json()

    assert body["repository"]["full_name"] == "encode/httpx"
    assert body["languages"] == {"Python": 570031, "Shell": 2821}
    assert len(body["contributors"]) == 2
    assert body["contributors_count"] == 2
    assert len(body["recent_commits"]) == 1
