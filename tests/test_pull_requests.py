"""Tests de Pull Requests Analysis.

El caso central es que "cerrado" y "mergeado" no son estados excluyentes: un
pull request mergeado esta cerrado y ademas tiene fecha de merge, asi que
cuenta en los dos contadores.
"""

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import github
from tests.conftest import successful_handler


def pr_crudo(
    number,
    title,
    state,
    login,
    merged_at=None,
    creado="2026-08-22T09:00:00Z",
    source="feature",
    target="main",
):
    """Construye un pull request con la forma que devuelve GET /pulls.

    Ojo con `merged_at`: el listado de GitHub no trae el campo "merged", asi
    que esta fecha es el unico rastro del merge.
    """
    return {
        "number": number,
        "title": title,
        "state": state,
        "user": {"login": login} if login else None,
        "created_at": creado,
        "updated_at": "2026-08-22T11:00:00Z",
        "merged_at": merged_at,
        "head": {"ref": source},
        "base": {"ref": target},
        "html_url": f"https://github.com/encode/httpx/pull/{number}",
    }


# Un abierto, un cerrado y mergeado, y un cerrado sin mergear.
MEZCLA = [
    pr_crudo(42, "Add issue analysis", "open", "SantiDev11", creado="2026-08-22T09:00:00Z"),
    pr_crudo(
        40,
        "Fix timeout handling",
        "closed",
        "tomchristie",
        merged_at="2026-08-21T09:30:00Z",
        creado="2026-08-20T10:00:00Z",
    ),
    pr_crudo(
        38,
        "Experimento descartado",
        "closed",
        "florimondmanca",
        creado="2026-08-18T08:00:00Z",
    ),
]


def responde_pulls(payload=None, status_code=200):
    """Manejador que controla /pulls y anota los parametros pedidos."""
    parametros = []

    def handler(request: httpx.Request) -> httpx.Response:
        if not request.url.path.endswith("/pulls"):
            return successful_handler(request)
        parametros.append(dict(request.url.params))
        if payload is None:
            return httpx.Response(status_code)
        return httpx.Response(status_code, json=payload)

    return handler, parametros


# --------------------------------------------------------------------------
# Casos correctos
# --------------------------------------------------------------------------


async def test_repositorio_con_varios_pull_requests(fake_github):
    handler, _ = responde_pulls(MEZCLA)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert [pr.number for pr in result.pull_requests] == [42, 40, 38]
    assert result.pull_requests_count == 3


async def test_pull_request_abierto(fake_github):
    handler, _ = responde_pulls([MEZCLA[0]])
    fake_github(handler)

    pr = (await github.analyze_repository("encode", "httpx")).pull_requests[0]

    assert pr.number == 42
    assert pr.title == "Add issue analysis"
    assert pr.state == "open"
    assert pr.author == "SantiDev11"
    assert pr.merged_at is None
    assert pr.source_branch == "feature"
    assert pr.target_branch == "main"
    assert pr.url == "https://github.com/encode/httpx/pull/42"


async def test_pull_request_cerrado_sin_mergear(fake_github):
    handler, _ = responde_pulls([MEZCLA[2]])
    fake_github(handler)

    pr = (await github.analyze_repository("encode", "httpx")).pull_requests[0]

    assert pr.state == "closed"
    assert pr.merged_at is None, "se cerro sin llegar a mergearse"


async def test_pull_request_mergeado(fake_github):
    handler, _ = responde_pulls([MEZCLA[1]])
    fake_github(handler)

    pr = (await github.analyze_repository("encode", "httpx")).pull_requests[0]

    assert pr.state == "closed", "GitHub no tiene un estado 'merged'"
    assert pr.merged_at is not None
    assert pr.merged_at.isoformat() == "2026-08-21T09:30:00+00:00"


async def test_se_piden_los_cerrados_tambien(fake_github):
    """Sin state=all GitHub devuelve solo los abiertos y no habria cerrados."""
    handler, parametros = responde_pulls(MEZCLA)
    fake_github(handler)

    await github.analyze_repository("encode", "httpx")

    assert parametros[0]["state"] == "all"


async def test_repositorio_sin_pull_requests_devuelve_lista_vacia(fake_github):
    handler, _ = responde_pulls([])
    fake_github(handler)

    result = await github.analyze_repository("alguien", "sin-pulls")

    assert result.pull_requests == []
    assert result.repository.name == "httpx", "el resto del analisis sigue ahi"


async def test_una_respuesta_vacia_deja_los_contadores_a_cero(fake_github):
    handler, _ = responde_pulls([])
    fake_github(handler)

    result = await github.analyze_repository("alguien", "sin-pulls")

    assert result.pull_requests_count == 0
    assert result.open_pull_requests_count == 0
    assert result.closed_pull_requests_count == 0
    assert result.merged_pull_requests_count == 0


# --------------------------------------------------------------------------
# Campos que GitHub puede dejar sin informar
# --------------------------------------------------------------------------


async def test_pull_request_sin_author_deja_el_campo_en_null(fake_github):
    """GitHub manda user=null si la cuenta que lo abrio fue borrada."""
    handler, _ = responde_pulls([pr_crudo(42, "Sin duenno", "open", None)])
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.pull_requests[0].author is None
    assert result.pull_requests_count == 1, "sigue contando como pull request"


async def test_un_pull_request_sin_author_no_tumba_a_los_demas(fake_github):
    handler, _ = responde_pulls([pr_crudo(42, "Sin duenno", "open", None), *MEZCLA])
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.pull_requests_count == 4
    assert [pr.author for pr in result.pull_requests].count(None) == 1


async def test_sin_ramas_los_campos_quedan_en_null(fake_github):
    """head y base pueden faltar si el fork de origen ya no existe."""
    crudo = pr_crudo(42, "Fork borrado", "open", "SantiDev11")
    del crudo["head"]
    del crudo["base"]
    handler, _ = responde_pulls([crudo])
    fake_github(handler)

    pr = (await github.analyze_repository("encode", "httpx")).pull_requests[0]

    assert pr.source_branch is None
    assert pr.target_branch is None
    assert pr.number == 42, "el resto del pull request se publica igual"


# --------------------------------------------------------------------------
# Errores
# --------------------------------------------------------------------------


async def test_repositorio_inexistente_lanza_not_found(fake_github):
    fake_github(lambda request: httpx.Response(404, json={"message": "Not Found"}))

    with pytest.raises(github.RepositoryNotFound):
        await github.analyze_repository("SantiDev11", "no-existe")


async def test_un_404_en_pulls_tambien_es_repositorio_inexistente(fake_github):
    """A diferencia de /issues: los pull requests no se pueden desactivar."""
    handler, _ = responde_pulls(payload={"message": "Not Found"}, status_code=404)
    fake_github(handler)

    with pytest.raises(github.RepositoryNotFound):
        await github.analyze_repository("SantiDev11", "no-existe")


async def test_error_de_la_api_de_github_lanza_github_error(fake_github):
    handler, _ = responde_pulls(payload={"message": "boom"}, status_code=500)
    fake_github(handler)

    with pytest.raises(github.GitHubError):
        await github.analyze_repository("encode", "httpx")


async def test_respuesta_inesperada_lanza_github_error(fake_github):
    """GitHub deberia mandar una lista; si manda otra cosa, error controlado."""
    handler, _ = responde_pulls({"message": "esto no es una lista"})
    fake_github(handler)

    with pytest.raises(github.GitHubError):
        await github.analyze_repository("encode", "httpx")


async def test_estado_desconocido_lanza_github_error(fake_github):
    """"merged" no es un estado de GitHub: solo existen open y closed."""
    handler, _ = responde_pulls([pr_crudo(42, "Raro", "merged", "SantiDev11")])
    fake_github(handler)

    with pytest.raises(github.GitHubError):
        await github.analyze_repository("encode", "httpx")


# --------------------------------------------------------------------------
# Contadores
# --------------------------------------------------------------------------


async def test_pull_requests_count_es_la_longitud_de_la_lista(fake_github):
    handler, _ = responde_pulls(MEZCLA)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.pull_requests_count == len(result.pull_requests) == 3


async def test_open_pull_requests_count(fake_github):
    handler, _ = responde_pulls(MEZCLA)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.open_pull_requests_count == 1


async def test_closed_pull_requests_count(fake_github):
    handler, _ = responde_pulls(MEZCLA)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.closed_pull_requests_count == 2, "el mergeado tambien esta cerrado"


async def test_merged_pull_requests_count(fake_github):
    handler, _ = responde_pulls(MEZCLA)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.merged_pull_requests_count == 1


async def test_un_pull_request_mergeado_cuenta_tambien_como_cerrado(fake_github):
    """El punto delicado de toda la funcionalidad, aislado en un solo test."""
    solo_mergeado = [
        pr_crudo(40, "Fix timeout", "closed", "tomchristie", merged_at="2026-08-21T09:30:00Z")
    ]
    handler, _ = responde_pulls(solo_mergeado)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.closed_pull_requests_count == 1
    assert result.merged_pull_requests_count == 1
    assert result.open_pull_requests_count == 0


async def test_cerrado_no_implica_mergeado(fake_github):
    """La otra mitad: cerrar sin mergear no debe sumar en los mergeados."""
    handler, _ = responde_pulls([pr_crudo(38, "Descartado", "closed", "SantiDev11")])
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.closed_pull_requests_count == 1
    assert result.merged_pull_requests_count == 0


async def test_abiertos_mas_cerrados_suman_el_total(fake_github):
    """Invariante: open y closed son excluyentes y no hay tercer estado."""
    handler, _ = responde_pulls(MEZCLA)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    suma = result.open_pull_requests_count + result.closed_pull_requests_count
    assert suma == result.pull_requests_count


async def test_los_mergeados_nunca_superan_a_los_cerrados(fake_github):
    """Invariante: merged es un subconjunto de closed, no un estado aparte."""
    handler, _ = responde_pulls(MEZCLA)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.merged_pull_requests_count <= result.closed_pull_requests_count


# --------------------------------------------------------------------------
# Orden
# --------------------------------------------------------------------------


async def test_se_pide_a_github_el_orden_por_fecha_descendente(fake_github):
    """Pedir el orden al servidor evita traerse los mas antiguos."""
    handler, parametros = responde_pulls(MEZCLA)
    fake_github(handler)

    await github.analyze_repository("encode", "httpx")

    assert parametros[0]["sort"] == "created"
    assert parametros[0]["direction"] == "desc"


async def test_se_devuelven_del_mas_reciente_al_mas_antiguo(fake_github):
    handler, _ = responde_pulls(MEZCLA)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    fechas = [pr.created_at for pr in result.pull_requests]
    assert fechas == sorted(fechas, reverse=True)


async def test_el_orden_se_garantiza_aunque_github_los_mande_desordenados(fake_github):
    """El orden es parte de nuestro contrato, no algo que confiemos a GitHub."""
    desordenados = [MEZCLA[2], MEZCLA[0], MEZCLA[1]]
    handler, _ = responde_pulls(desordenados)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert [pr.number for pr in result.pull_requests] == [42, 40, 38]


# --------------------------------------------------------------------------
# Modelo y limite
# --------------------------------------------------------------------------


async def test_solo_se_devuelven_los_campos_de_nuestro_modelo(fake_github):
    """GitHub manda decenas de campos por pull request; publicamos diez."""
    crudo = {
        **MEZCLA[0],
        "node_id": "PR_kwDO",
        "body": "Un cuerpo larguisimo que no queremos publicar",
        "labels": [{"name": "enhancement"}],
        "draft": False,
        "diff_url": "https://github.com/encode/httpx/pull/42.diff",
        "_links": {"self": {"href": "..."}},
        "author_association": "OWNER",
    }
    handler, _ = responde_pulls([crudo])
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert set(result.pull_requests[0].model_dump()) == {
        "number",
        "title",
        "state",
        "author",
        "created_at",
        "updated_at",
        "merged_at",
        "source_branch",
        "target_branch",
        "url",
    }


async def test_por_defecto_se_piden_diez_pull_requests(fake_github):
    handler, parametros = responde_pulls(MEZCLA)
    fake_github(handler)

    await github.analyze_repository("encode", "httpx")

    assert parametros[0]["per_page"] == "10"


async def test_el_limite_pedido_llega_a_github(fake_github):
    handler, parametros = responde_pulls(MEZCLA)
    fake_github(handler)

    await github.analyze_repository("encode", "httpx", pulls_limit=40)

    assert parametros[0]["per_page"] == "40"


async def test_limites_distintos_no_comparten_cache(fake_github):
    handler, parametros = responde_pulls(MEZCLA)
    fake_github(handler)

    await github.analyze_repository("encode", "httpx", pulls_limit=10)
    await github.analyze_repository("encode", "httpx", pulls_limit=40)

    assert [p["per_page"] for p in parametros] == ["10", "40"]


async def test_el_mismo_limite_reutiliza_la_cache(fake_github):
    """La clave de cache crecio: hay que comprobar que sigue acertando."""
    handler, _ = responde_pulls(MEZCLA)
    fake_github(handler)

    primero = await github.analyze_repository("encode", "httpx", pulls_limit=5)
    segundo = await github.analyze_repository("encode", "httpx", pulls_limit=5)

    assert primero.cached is False
    assert segundo.cached is True


async def test_los_limites_anteriores_siguen_funcionando(fake_github):
    """Anadir #pulls a la clave no debe romper commits ni issues."""
    handler, parametros = responde_pulls(MEZCLA)
    fake_github(handler)

    await github.analyze_repository("encode", "httpx", commits_limit=5, issues_limit=7)
    segundo = await github.analyze_repository(
        "encode", "httpx", commits_limit=5, issues_limit=7
    )

    assert len(parametros) == 1, "el segundo analisis sale de la cache"
    assert segundo.cached is True


# --------------------------------------------------------------------------
# Integracion por HTTP
# --------------------------------------------------------------------------


def test_integracion_con_el_endpoint_analyze(fake_github):
    handler, _ = responde_pulls(MEZCLA)
    fake_github(handler)

    response = TestClient(app).get("/analyze/encode/httpx")

    assert response.status_code == 200
    body = response.json()
    assert body["pull_requests_count"] == 3
    assert body["open_pull_requests_count"] == 1
    assert body["closed_pull_requests_count"] == 2
    assert body["merged_pull_requests_count"] == 1
    assert body["pull_requests"][1] == {
        "number": 40,
        "title": "Fix timeout handling",
        "state": "closed",
        "author": "tomchristie",
        "created_at": "2026-08-20T10:00:00Z",
        "updated_at": "2026-08-22T11:00:00Z",
        "merged_at": "2026-08-21T09:30:00Z",
        "source_branch": "feature",
        "target_branch": "main",
        "url": "https://github.com/encode/httpx/pull/40",
    }


def test_integracion_el_parametro_pulls_llega_a_github(fake_github):
    handler, parametros = responde_pulls(MEZCLA)
    fake_github(handler)

    response = TestClient(app).get("/analyze/encode/httpx?pulls=3")

    assert response.status_code == 200
    assert parametros[0]["per_page"] == "3"


@pytest.mark.parametrize("valor", [0, -1, 101, 5000])
def test_integracion_cantidades_fuera_de_rango_devuelven_422(fake_github, valor):
    handler, parametros = responde_pulls(MEZCLA)
    fake_github(handler)

    response = TestClient(app).get(f"/analyze/encode/httpx?pulls={valor}")

    assert response.status_code == 422
    assert parametros == [], "no se llega a consultar GitHub"


def test_integracion_las_funcionalidades_anteriores_siguen_ahi(fake_github):
    """Pull requests no debe haber desplazado nada de lo que ya devolviamos."""
    handler, _ = responde_pulls(MEZCLA)
    fake_github(handler)

    body = TestClient(app).get("/analyze/encode/httpx").json()

    assert body["repository"]["full_name"] == "encode/httpx"
    assert body["languages"] == {"Python": 570031, "Shell": 2821}
    assert body["contributors_count"] == 2
    assert len(body["recent_commits"]) == 1
    assert body["issues_count"] == 2
    assert body["open_issues_count"] == 1
    assert body["closed_issues_count"] == 1
    assert body["latest_release"]["tag"] == "0.28.1"
