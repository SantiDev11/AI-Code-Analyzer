"""Tests de Repository Activity Analysis.

Activity no consulta GitHub: reparte por dia los commits, issues, pull
requests y releases que el analisis ya trae. Estos tests comprueban sobre todo
el agrupamiento por dia UTC y que no aparece ninguna peticion nueva.

El reloj se sustituye en todos los tests que miran fechas: si dependieran del
dia real, dejarian de pasar manana.
"""

from datetime import UTC, datetime

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import github
from tests.conftest import successful_handler

# Instante fijo desde el que se mide la ventana en todos los tests.
AHORA = datetime(2026, 8, 22, 12, 0, 0, tzinfo=UTC)
HOY = "2026-08-22"
AYER = "2026-08-21"


@pytest.fixture
def reloj_fijo(monkeypatch):
    """Congela el ahora del servicio para que la ventana sea reproducible."""
    monkeypatch.setattr(github, "_utc_now", lambda: AHORA)
    return AHORA


def commit_crudo(sha, fecha, mensaje="Un commit", login="SantiDev11"):
    return {
        "sha": sha,
        "html_url": f"https://github.com/encode/httpx/commit/{sha}",
        "author": {"login": login},
        "commit": {"message": mensaje, "author": {"name": "Kevin", "date": fecha}},
    }


def issue_crudo(number, creado, login="SantiDev11"):
    return {
        "number": number,
        "title": f"Issue {number}",
        "state": "open",
        "user": {"login": login},
        "created_at": creado,
        "updated_at": creado,
        "html_url": f"https://github.com/encode/httpx/issues/{number}",
    }


def pr_crudo(number, creado, cerrado=None, state="open", login="SantiDev11"):
    return {
        "number": number,
        "title": f"PR {number}",
        "state": state,
        "user": {"login": login},
        "created_at": creado,
        "updated_at": creado,
        "closed_at": cerrado,
        "merged_at": None,
        "head": {"ref": "feature"},
        "base": {"ref": "main"},
        "html_url": f"https://github.com/encode/httpx/pull/{number}",
    }


def release_crudo(identificador, tag, publicado, draft=False):
    return {
        "id": identificador,
        "tag_name": tag,
        "name": tag,
        "body": None,
        "draft": draft,
        "prerelease": False,
        "created_at": "2026-08-01T00:00:00Z",
        "published_at": publicado,
        "author": {"login": "SantiDev11"},
        "html_url": f"https://github.com/encode/httpx/releases/tag/{tag}",
    }


def responde(commits=None, issues=None, pulls=None, releases=None):
    """Manejador que sustituye solo las listas que se le pasan.

    Lo que no se indica lo sirve el manejador comun, asi el resto del analisis
    sigue funcionando con normalidad.
    """

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/commits") and commits is not None:
            return httpx.Response(200, json=commits)
        if path.endswith("/issues") and issues is not None:
            return httpx.Response(200, json=issues)
        if path.endswith("/pulls") and pulls is not None:
            return httpx.Response(200, json=pulls)
        # /releases/latest no termina en /releases, asi que no se cruza.
        if path.endswith("/releases") and releases is not None:
            return httpx.Response(200, json=releases)
        return successful_handler(request)

    return handler


def vacio():
    """Un repositorio que existe pero no tiene nada que contar."""
    return responde(commits=[], issues=[], pulls=[], releases=[])


def por_dia(activity):
    """{fecha: recuentos} para comprobar dias sueltos con comodidad."""
    return {str(dia.date): dia for dia in activity.daily}


# --------------------------------------------------------------------------
# Repositorio con actividad y casos vacios
# --------------------------------------------------------------------------


async def test_repositorio_con_actividad(fake_github, reloj_fijo):
    fake_github(
        responde(
            commits=[commit_crudo("aaa1111", f"{HOY}T09:00:00Z")],
            issues=[issue_crudo(1, f"{HOY}T10:00:00Z")],
            pulls=[pr_crudo(2, f"{HOY}T11:00:00Z")],
            releases=[release_crudo(300, "1.0.0", f"{HOY}T08:00:00Z")],
        )
    )

    activity = (await github.analyze_repository("encode", "httpx")).activity

    assert activity.total_commits == 1
    assert activity.total_issues == 1
    assert activity.total_pull_requests == 1
    assert activity.total_releases == 1
    assert len(activity.daily) == 1
    assert str(activity.daily[0].date) == HOY


async def test_repositorio_sin_issues(fake_github, reloj_fijo):
    fake_github(
        responde(
            commits=[commit_crudo("aaa1111", f"{HOY}T09:00:00Z")],
            issues=[],
            pulls=[pr_crudo(2, f"{HOY}T11:00:00Z")],
            releases=[],
        )
    )

    activity = (await github.analyze_repository("encode", "httpx")).activity

    assert activity.total_issues == 0
    assert activity.total_commits == 1, "lo demas se sigue contando"
    assert por_dia(activity)[HOY].issues == 0


async def test_repositorio_sin_pull_requests(fake_github, reloj_fijo):
    fake_github(
        responde(
            commits=[commit_crudo("aaa1111", f"{HOY}T09:00:00Z")],
            issues=[issue_crudo(1, f"{HOY}T10:00:00Z")],
            pulls=[],
            releases=[],
        )
    )

    activity = (await github.analyze_repository("encode", "httpx")).activity

    assert activity.total_pull_requests == 0
    assert por_dia(activity)[HOY].pull_requests_opened == 0
    assert por_dia(activity)[HOY].pull_requests_closed == 0


async def test_repositorio_sin_releases(fake_github, reloj_fijo):
    fake_github(
        responde(
            commits=[commit_crudo("aaa1111", f"{HOY}T09:00:00Z")],
            issues=[],
            pulls=[],
            releases=[],
        )
    )

    activity = (await github.analyze_repository("encode", "httpx")).activity

    assert activity.total_releases == 0
    assert por_dia(activity)[HOY].releases == 0


async def test_sin_datos_la_actividad_queda_vacia(fake_github, reloj_fijo):
    """Un repositorio recien creado no debe romper nada."""
    fake_github(vacio())

    activity = (await github.analyze_repository("alguien", "vacio")).activity

    assert activity.daily == []
    assert activity.total_commits == 0
    assert activity.total_issues == 0
    assert activity.total_pull_requests == 0
    assert activity.total_releases == 0
    assert str(activity.until) == HOY, "el periodo se describe igualmente"


# --------------------------------------------------------------------------
# Agrupamiento por dia
# --------------------------------------------------------------------------


async def test_actividad_repartida_en_varios_dias(fake_github, reloj_fijo):
    fake_github(
        responde(
            commits=[
                commit_crudo("aaa1111", f"{HOY}T09:00:00Z"),
                commit_crudo("bbb2222", f"{AYER}T09:00:00Z"),
                commit_crudo("ccc3333", "2026-08-20T09:00:00Z"),
            ],
            issues=[],
            pulls=[],
            releases=[],
        )
    )

    activity = (await github.analyze_repository("encode", "httpx")).activity

    assert [str(dia.date) for dia in activity.daily] == [HOY, AYER, "2026-08-20"]
    assert activity.total_commits == 3


async def test_los_commits_del_mismo_dia_se_suman(fake_github, reloj_fijo):
    fake_github(
        responde(
            commits=[
                commit_crudo("aaa1111", f"{HOY}T09:00:00Z"),
                commit_crudo("bbb2222", f"{HOY}T18:45:00Z"),
                commit_crudo("ccc3333", f"{AYER}T23:59:00Z"),
            ],
            issues=[],
            pulls=[],
            releases=[],
        )
    )

    activity = (await github.analyze_repository("encode", "httpx")).activity

    assert por_dia(activity)[HOY].commits == 2
    assert por_dia(activity)[AYER].commits == 1


async def test_los_issues_se_agrupan_por_su_fecha_de_creacion(fake_github, reloj_fijo):
    fake_github(
        responde(
            commits=[],
            issues=[
                issue_crudo(1, f"{HOY}T10:00:00Z"),
                issue_crudo(2, f"{AYER}T10:00:00Z"),
                issue_crudo(3, f"{AYER}T20:00:00Z"),
            ],
            pulls=[],
            releases=[],
        )
    )

    activity = (await github.analyze_repository("encode", "httpx")).activity

    assert por_dia(activity)[HOY].issues == 1
    assert por_dia(activity)[AYER].issues == 2


async def test_los_pull_requests_abiertos_y_cerrados_van_por_separado(
    fake_github, reloj_fijo
):
    """Un PR abierto ayer y cerrado hoy suma en dos dias distintos."""
    fake_github(
        responde(
            commits=[],
            issues=[],
            pulls=[
                pr_crudo(1, f"{AYER}T09:00:00Z", cerrado=f"{HOY}T09:00:00Z", state="closed"),
                pr_crudo(2, f"{HOY}T10:00:00Z"),
            ],
            releases=[],
        )
    )

    activity = (await github.analyze_repository("encode", "httpx")).activity

    assert por_dia(activity)[AYER].pull_requests_opened == 1
    assert por_dia(activity)[AYER].pull_requests_closed == 0
    assert por_dia(activity)[HOY].pull_requests_opened == 1
    assert por_dia(activity)[HOY].pull_requests_closed == 1


async def test_un_pull_request_cerrado_sin_mergear_tambien_cuenta(
    fake_github, reloj_fijo
):
    """merged_at es null aqui: sin closed_at el cierre se perderia."""
    fake_github(
        responde(
            commits=[],
            issues=[],
            pulls=[pr_crudo(1, f"{AYER}T09:00:00Z", cerrado=f"{HOY}T09:00:00Z", state="closed")],
            releases=[],
        )
    )

    activity = (await github.analyze_repository("encode", "httpx")).activity

    assert por_dia(activity)[HOY].pull_requests_closed == 1


async def test_los_releases_se_agrupan_por_su_fecha_de_publicacion(
    fake_github, reloj_fijo
):
    fake_github(
        responde(
            commits=[],
            issues=[],
            pulls=[],
            releases=[
                release_crudo(300, "1.0.0", f"{HOY}T08:00:00Z"),
                release_crudo(290, "0.9.0", f"{AYER}T08:00:00Z"),
            ],
        )
    )

    activity = (await github.analyze_repository("encode", "httpx")).activity

    assert por_dia(activity)[HOY].releases == 1
    assert por_dia(activity)[AYER].releases == 1
    assert activity.total_releases == 2


async def test_un_borrador_no_cuenta_como_release_publicado(fake_github, reloj_fijo):
    """published_at es null en un borrador: nunca se publico."""
    fake_github(
        responde(
            commits=[],
            issues=[],
            pulls=[],
            releases=[
                release_crudo(300, "1.0.0", f"{HOY}T08:00:00Z"),
                release_crudo(280, "2.0.0", None, draft=True),
            ],
        )
    )

    result = await github.analyze_repository("encode", "httpx")

    assert result.activity.total_releases == 1
    assert result.releases_count == 2, "pero sigue estando en la lista de releases"


async def test_los_dias_sin_actividad_no_aparecen(fake_github, reloj_fijo):
    fake_github(
        responde(
            commits=[
                commit_crudo("aaa1111", f"{HOY}T09:00:00Z"),
                commit_crudo("bbb2222", "2026-08-15T09:00:00Z"),
            ],
            issues=[],
            pulls=[],
            releases=[],
        )
    )

    activity = (await github.analyze_repository("encode", "httpx")).activity

    assert [str(dia.date) for dia in activity.daily] == [HOY, "2026-08-15"]


async def test_los_dias_vienen_del_mas_reciente_al_mas_antiguo(fake_github, reloj_fijo):
    fake_github(
        responde(
            commits=[
                commit_crudo("aaa1111", "2026-08-18T09:00:00Z"),
                commit_crudo("bbb2222", f"{HOY}T09:00:00Z"),
                commit_crudo("ccc3333", "2026-08-20T09:00:00Z"),
            ],
            issues=[],
            pulls=[],
            releases=[],
        )
    )

    activity = (await github.analyze_repository("encode", "httpx")).activity

    fechas = [dia.date for dia in activity.daily]
    assert fechas == sorted(fechas, reverse=True)


# --------------------------------------------------------------------------
# Fechas y UTC
# --------------------------------------------------------------------------


async def test_las_fechas_se_agrupan_en_utc(fake_github, reloj_fijo):
    """Un commit a las 23:30 UTC pertenece a ese dia, no al siguiente."""
    fake_github(
        responde(
            commits=[
                commit_crudo("aaa1111", f"{AYER}T23:30:00Z"),
                commit_crudo("bbb2222", f"{HOY}T00:30:00Z"),
            ],
            issues=[],
            pulls=[],
            releases=[],
        )
    )

    activity = (await github.analyze_repository("encode", "httpx")).activity

    assert por_dia(activity)[AYER].commits == 1
    assert por_dia(activity)[HOY].commits == 1


async def test_una_fecha_con_otro_huso_se_convierte_a_utc(fake_github, reloj_fijo):
    """2026-08-23T01:00+03:00 son las 22:00 UTC del 22: cuenta como dia 22."""
    fake_github(
        responde(
            commits=[commit_crudo("aaa1111", "2026-08-23T01:00:00+03:00")],
            issues=[],
            pulls=[],
            releases=[],
        )
    )

    activity = (await github.analyze_repository("encode", "httpx")).activity

    assert [str(dia.date) for dia in activity.daily] == [HOY]


# --------------------------------------------------------------------------
# Rango temporal
# --------------------------------------------------------------------------


async def test_el_periodo_se_describe_en_la_respuesta(fake_github, reloj_fijo):
    fake_github(vacio())

    activity = (await github.analyze_repository("encode", "httpx")).activity

    assert activity.days == 30
    assert str(activity.until) == HOY
    assert str(activity.since) == "2026-07-24", "30 dias contando hoy"


async def test_el_rango_temporal_es_configurable(fake_github, reloj_fijo):
    fake_github(vacio())

    activity = (
        await github.analyze_repository("encode", "httpx", activity_days=7)
    ).activity

    assert activity.days == 7
    assert str(activity.since) == "2026-08-16"
    assert str(activity.until) == HOY


async def test_una_ventana_de_un_dia_es_solo_hoy(fake_github, reloj_fijo):
    fake_github(vacio())

    activity = (
        await github.analyze_repository("encode", "httpx", activity_days=1)
    ).activity

    assert str(activity.since) == str(activity.until) == HOY


async def test_lo_anterior_a_la_ventana_queda_fuera(fake_github, reloj_fijo):
    fake_github(
        responde(
            commits=[
                commit_crudo("aaa1111", f"{HOY}T09:00:00Z"),
                commit_crudo("bbb2222", "2026-01-01T09:00:00Z"),
            ],
            issues=[],
            pulls=[],
            releases=[],
        )
    )

    activity = (await github.analyze_repository("encode", "httpx")).activity

    assert activity.total_commits == 1, "el commit de enero cae fuera de los 30 dias"
    assert [str(dia.date) for dia in activity.daily] == [HOY]


async def test_el_borde_de_la_ventana_entra(fake_github, reloj_fijo):
    """El primer dia del periodo esta incluido, no excluido."""
    fake_github(
        responde(
            commits=[commit_crudo("aaa1111", "2026-08-16T00:00:00Z")],
            issues=[],
            pulls=[],
            releases=[],
        )
    )

    activity = (
        await github.analyze_repository("encode", "httpx", activity_days=7)
    ).activity

    assert activity.total_commits == 1
    assert [str(dia.date) for dia in activity.daily] == ["2026-08-16"]


async def test_ventanas_distintas_no_comparten_cache(fake_github, reloj_fijo):
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        return successful_handler(request)

    fake_github(handler)

    await github.analyze_repository("encode", "httpx", activity_days=7)
    await github.analyze_repository("encode", "httpx", activity_days=30)

    assert len(calls) == 18, "cada ventana vuelve a calcular el analisis"


# --------------------------------------------------------------------------
# Totales
# --------------------------------------------------------------------------


async def test_total_commits(fake_github, reloj_fijo):
    fake_github(
        responde(
            commits=[
                commit_crudo("aaa1111", f"{HOY}T09:00:00Z"),
                commit_crudo("bbb2222", f"{AYER}T09:00:00Z"),
            ],
            issues=[],
            pulls=[],
            releases=[],
        )
    )

    assert (await github.analyze_repository("encode", "httpx")).activity.total_commits == 2


async def test_total_issues(fake_github, reloj_fijo):
    fake_github(
        responde(
            commits=[],
            issues=[issue_crudo(1, f"{HOY}T10:00:00Z"), issue_crudo(2, f"{AYER}T10:00:00Z")],
            pulls=[],
            releases=[],
        )
    )

    assert (await github.analyze_repository("encode", "httpx")).activity.total_issues == 2


async def test_total_pull_requests_cuenta_los_abiertos(fake_github, reloj_fijo):
    """Un PR abierto y cerrado dentro del periodo cuenta una vez, no dos."""
    fake_github(
        responde(
            commits=[],
            issues=[],
            pulls=[
                pr_crudo(1, f"{AYER}T09:00:00Z", cerrado=f"{HOY}T09:00:00Z", state="closed"),
                pr_crudo(2, f"{HOY}T10:00:00Z"),
            ],
            releases=[],
        )
    )

    activity = (await github.analyze_repository("encode", "httpx")).activity

    assert activity.total_pull_requests == 2


async def test_total_releases(fake_github, reloj_fijo):
    fake_github(
        responde(
            commits=[],
            issues=[],
            pulls=[],
            releases=[release_crudo(300, "1.0.0", f"{HOY}T08:00:00Z")],
        )
    )

    assert (await github.analyze_repository("encode", "httpx")).activity.total_releases == 1


async def test_los_totales_coinciden_con_la_suma_diaria(fake_github, reloj_fijo):
    """Invariante: los totales salen de sumar daily, no pueden discrepar."""
    fake_github(
        responde(
            commits=[
                commit_crudo("aaa1111", f"{HOY}T09:00:00Z"),
                commit_crudo("bbb2222", f"{AYER}T09:00:00Z"),
            ],
            issues=[issue_crudo(1, f"{HOY}T10:00:00Z")],
            pulls=[pr_crudo(2, f"{AYER}T11:00:00Z")],
            releases=[release_crudo(300, "1.0.0", f"{HOY}T08:00:00Z")],
        )
    )

    activity = (await github.analyze_repository("encode", "httpx")).activity

    assert activity.total_commits == sum(dia.commits for dia in activity.daily)
    assert activity.total_issues == sum(dia.issues for dia in activity.daily)
    assert activity.total_pull_requests == sum(
        dia.pull_requests_opened for dia in activity.daily
    )
    assert activity.total_releases == sum(dia.releases for dia in activity.daily)


# --------------------------------------------------------------------------
# Sin peticiones extra
# --------------------------------------------------------------------------


async def test_activity_no_anade_ninguna_llamada_a_github(fake_github, reloj_fijo):
    """El punto central del disenno: Activity sale de datos ya descargados."""
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        return successful_handler(request)

    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert len(calls) == 9, "los mismos 9 endpoints con Git Tree"
    assert result.activity is not None


# --------------------------------------------------------------------------
# Integracion por HTTP
# --------------------------------------------------------------------------


def test_integracion_con_el_endpoint_analyze(fake_github, reloj_fijo):
    fake_github(
        responde(
            commits=[commit_crudo("aaa1111", f"{HOY}T09:00:00Z")],
            issues=[issue_crudo(1, f"{HOY}T10:00:00Z")],
            pulls=[pr_crudo(2, f"{HOY}T11:00:00Z")],
            releases=[release_crudo(300, "1.0.0", f"{HOY}T08:00:00Z")],
        )
    )

    response = TestClient(app).get("/analyze/encode/httpx")

    assert response.status_code == 200
    assert response.json()["activity"] == {
        "days": 30,
        "since": "2026-07-24",
        "until": HOY,
        "total_commits": 1,
        "total_issues": 1,
        "total_pull_requests": 1,
        "total_releases": 1,
        "daily": [
            {
                "date": HOY,
                "commits": 1,
                "issues": 1,
                "pull_requests_opened": 1,
                "pull_requests_closed": 0,
                "releases": 1,
            }
        ],
    }


def test_integracion_el_parametro_activity_days_llega_al_analisis(
    fake_github, reloj_fijo
):
    fake_github(vacio())

    body = TestClient(app).get("/analyze/encode/httpx?activity_days=7").json()

    assert body["activity"]["days"] == 7
    assert body["activity"]["since"] == "2026-08-16"


@pytest.mark.parametrize("valor", [0, -1, 366, 5000])
def test_integracion_ventanas_fuera_de_rango_devuelven_422(
    fake_github, reloj_fijo, valor
):
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        return successful_handler(request)

    fake_github(handler)

    response = TestClient(app).get(f"/analyze/encode/httpx?activity_days={valor}")

    assert response.status_code == 422
    assert calls == [], "no se llega a consultar GitHub"


def test_integracion_las_funcionalidades_anteriores_siguen_ahi(fake_github, reloj_fijo):
    """Activity no debe haber desplazado nada de lo que ya devolviamos."""
    fake_github(successful_handler)

    body = TestClient(app).get("/analyze/encode/httpx").json()

    assert body["repository"]["full_name"] == "encode/httpx"
    assert body["languages"] == {"Python": 570031, "Shell": 2821}
    assert body["contributors_count"] == 2
    assert len(body["recent_commits"]) == 1
    assert body["issues_count"] == 2
    assert body["pull_requests_count"] == 3
    assert body["releases_count"] == 3
    assert body["latest_release"]["tag"] == "0.28.1"
