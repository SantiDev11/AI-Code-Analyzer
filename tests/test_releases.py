"""Tests de Releases Analysis.

El caso central es que `draft` y `prerelease` son dos indicadores
independientes, no tres estados: publicado significa exactamente "no es un
borrador", asi que una version previa publicada cuenta a la vez en los
publicados y en las prereleases.
"""

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import github
from tests.conftest import successful_handler


def release_crudo(
    identificador,
    tag,
    name="Version",
    body="Notas de la version",
    draft=False,
    prerelease=False,
    login="tomchristie",
    creado="2024-12-06T15:00:00Z",
    publicado="2024-12-06T15:36:24Z",
):
    """Construye un release con la forma que devuelve GET /releases.

    Un borrador no tiene fecha de publicacion, asi que quien pase draft=True
    normalmente querra pasar tambien publicado=None.
    """
    return {
        "id": identificador,
        "tag_name": tag,
        "name": name,
        "body": body,
        "draft": draft,
        "prerelease": prerelease,
        "created_at": creado,
        "published_at": publicado,
        "author": {"login": login} if login else None,
        "html_url": f"https://github.com/encode/httpx/releases/tag/{tag}",
    }


# Un publicado estable, un publicado marcado como version previa y un borrador.
MEZCLA = [
    release_crudo(300, "0.28.1", name="Version 0.28.1"),
    release_crudo(290, "0.29.0rc1", name="Version 0.29.0 rc1", prerelease=True),
    release_crudo(280, "0.30.0", name=None, draft=True, publicado=None),
]


def responde_releases(payload=None, status_code=200):
    """Manejador que controla /releases y anota los parametros pedidos.

    Deja pasar /releases/latest, que es otro endpoint y alimenta el campo
    `latest_release` que ya existia.
    """
    parametros = []

    def handler(request: httpx.Request) -> httpx.Response:
        if not request.url.path.endswith("/releases"):
            return successful_handler(request)
        parametros.append(dict(request.url.params))
        if payload is None:
            return httpx.Response(status_code)
        return httpx.Response(status_code, json=payload)

    return handler, parametros


# --------------------------------------------------------------------------
# Casos correctos
# --------------------------------------------------------------------------


async def test_repositorio_con_varios_releases(fake_github):
    handler, _ = responde_releases(MEZCLA)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert [r.tag_name for r in result.releases] == ["0.28.1", "0.29.0rc1", "0.30.0"]
    assert result.releases_count == 3


async def test_release_publicado(fake_github):
    handler, _ = responde_releases([MEZCLA[0]])
    fake_github(handler)

    release = (await github.analyze_repository("encode", "httpx")).releases[0]

    assert release.id == 300
    assert release.tag_name == "0.28.1"
    assert release.name == "Version 0.28.1"
    assert release.body == "Notas de la version"
    assert release.draft is False
    assert release.prerelease is False
    assert release.author == "tomchristie"
    assert release.published_at is not None
    assert release.url == "https://github.com/encode/httpx/releases/tag/0.28.1"


async def test_draft_release(fake_github):
    handler, _ = responde_releases([MEZCLA[2]])
    fake_github(handler)

    release = (await github.analyze_repository("encode", "httpx")).releases[0]

    assert release.draft is True
    assert release.prerelease is False, "ser borrador no lo hace version previa"
    assert release.published_at is None, "un borrador no se ha publicado nunca"
    assert release.created_at is not None, "pero si tiene fecha de creacion"


async def test_prerelease(fake_github):
    handler, _ = responde_releases([MEZCLA[1]])
    fake_github(handler)

    release = (await github.analyze_repository("encode", "httpx")).releases[0]

    assert release.prerelease is True
    assert release.draft is False, "una version previa si esta publicada"
    assert release.published_at is not None


async def test_un_prerelease_no_es_un_draft(fake_github):
    """Los dos indicadores viajan por separado en el mismo release."""
    handler, _ = responde_releases(MEZCLA)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    por_tag = {r.tag_name: r for r in result.releases}
    assert (por_tag["0.29.0rc1"].prerelease, por_tag["0.29.0rc1"].draft) == (True, False)
    assert (por_tag["0.30.0"].prerelease, por_tag["0.30.0"].draft) == (False, True)


# --------------------------------------------------------------------------
# Campos que GitHub puede dejar sin informar
# --------------------------------------------------------------------------


async def test_release_sin_author_deja_el_campo_en_null(fake_github):
    handler, _ = responde_releases([release_crudo(300, "1.0.0", login=None)])
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.releases[0].author is None
    assert result.releases_count == 1, "sigue contando como release"


async def test_release_sin_name_deja_el_campo_en_null(fake_github):
    handler, _ = responde_releases([release_crudo(300, "1.0.0", name=None)])
    fake_github(handler)

    release = (await github.analyze_repository("encode", "httpx")).releases[0]

    assert release.name is None
    assert release.tag_name == "1.0.0", "la etiqueta si es obligatoria"


async def test_release_sin_body_deja_el_campo_en_null(fake_github):
    handler, _ = responde_releases([release_crudo(300, "1.0.0", body=None)])
    fake_github(handler)

    assert (await github.analyze_repository("encode", "httpx")).releases[0].body is None


async def test_sin_campos_opcionales_no_tumba_a_los_demas(fake_github):
    """Faltando las claves enteras, no solo con valor null."""
    crudo = release_crudo(300, "1.0.0")
    del crudo["name"]
    del crudo["body"]
    del crudo["author"]
    handler, _ = responde_releases([crudo, *MEZCLA])
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.releases_count == 4
    assert (result.releases[0].name, result.releases[0].body) == (None, None)
    assert result.releases[0].author is None


# --------------------------------------------------------------------------
# Repositorio sin releases
# --------------------------------------------------------------------------


async def test_repositorio_sin_releases_devuelve_lista_vacia(fake_github):
    handler, _ = responde_releases([])
    fake_github(handler)

    result = await github.analyze_repository("alguien", "sin-releases")

    assert result.releases == []
    assert result.repository.name == "httpx", "el resto del analisis sigue ahi"


async def test_una_respuesta_vacia_deja_los_contadores_a_cero(fake_github):
    handler, _ = responde_releases([])
    fake_github(handler)

    result = await github.analyze_repository("alguien", "sin-releases")

    assert result.releases_count == 0
    assert result.published_releases_count == 0
    assert result.draft_releases_count == 0
    assert result.prereleases_count == 0


# --------------------------------------------------------------------------
# Errores
# --------------------------------------------------------------------------


async def test_repositorio_inexistente_lanza_not_found(fake_github):
    fake_github(lambda request: httpx.Response(404, json={"message": "Not Found"}))

    with pytest.raises(github.RepositoryNotFound):
        await github.analyze_repository("SantiDev11", "no-existe")


async def test_un_404_en_releases_es_repositorio_inexistente(fake_github):
    """A diferencia de /releases/latest, donde el 404 significa 'no hay'."""
    handler, _ = responde_releases(payload={"message": "Not Found"}, status_code=404)
    fake_github(handler)

    with pytest.raises(github.RepositoryNotFound):
        await github.analyze_repository("SantiDev11", "no-existe")


async def test_error_de_la_api_de_github_lanza_github_error(fake_github):
    handler, _ = responde_releases(payload={"message": "boom"}, status_code=500)
    fake_github(handler)

    with pytest.raises(github.GitHubError):
        await github.analyze_repository("encode", "httpx")


async def test_respuesta_inesperada_lanza_github_error(fake_github):
    """GitHub deberia mandar una lista; si manda otra cosa, error controlado."""
    handler, _ = responde_releases({"message": "esto no es una lista"})
    fake_github(handler)

    with pytest.raises(github.GitHubError):
        await github.analyze_repository("encode", "httpx")


async def test_release_sin_tag_lanza_github_error(fake_github):
    """tag_name no es opcional: un release sin etiqueta no es representable."""
    crudo = release_crudo(300, "1.0.0")
    del crudo["tag_name"]
    handler, _ = responde_releases([crudo])
    fake_github(handler)

    with pytest.raises(github.GitHubError):
        await github.analyze_repository("encode", "httpx")


# --------------------------------------------------------------------------
# Contadores
# --------------------------------------------------------------------------


async def test_releases_count_es_la_longitud_de_la_lista(fake_github):
    handler, _ = responde_releases(MEZCLA)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.releases_count == len(result.releases) == 3


async def test_published_releases_count(fake_github):
    handler, _ = responde_releases(MEZCLA)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.published_releases_count == 2, "la version previa tambien esta publicada"


async def test_draft_releases_count(fake_github):
    handler, _ = responde_releases(MEZCLA)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.draft_releases_count == 1


async def test_prereleases_count(fake_github):
    handler, _ = responde_releases(MEZCLA)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.prereleases_count == 1


async def test_un_prerelease_publicado_cuenta_en_los_dos(fake_github):
    """El punto delicado, aislado: publicado y version previa a la vez."""
    handler, _ = responde_releases([release_crudo(290, "1.0.0rc1", prerelease=True)])
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.published_releases_count == 1
    assert result.prereleases_count == 1
    assert result.draft_releases_count == 0


async def test_un_draft_no_cuenta_como_publicado(fake_github):
    """La otra mitad: un borrador no esta publicado por mucho que exista."""
    handler, _ = responde_releases([release_crudo(280, "1.0.0", draft=True, publicado=None)])
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.draft_releases_count == 1
    assert result.published_releases_count == 0
    assert result.releases_count == 1, "pero sigue estando en la lista"


async def test_publicados_mas_borradores_suman_el_total(fake_github):
    """Invariante: publicado es exactamente lo contrario de borrador."""
    handler, _ = responde_releases(MEZCLA)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    suma = result.published_releases_count + result.draft_releases_count
    assert suma == result.releases_count


async def test_un_borrador_marcado_como_version_previa(fake_github):
    """GitHub lo permite: cuenta en borradores y en prereleases, no publicado."""
    raro = release_crudo(270, "2.0.0rc1", draft=True, prerelease=True, publicado=None)
    handler, _ = responde_releases([raro])
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.draft_releases_count == 1
    assert result.prereleases_count == 1
    assert result.published_releases_count == 0


# --------------------------------------------------------------------------
# Orden
# --------------------------------------------------------------------------


async def test_se_respeta_el_orden_de_github(fake_github):
    """No reordenamos: los borradores no tienen fecha de publicacion con la
    que compararlos, asi que el orden de GitHub es el unico honesto."""
    al_reves = [MEZCLA[2], MEZCLA[1], MEZCLA[0]]
    handler, _ = responde_releases(al_reves)
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert [r.tag_name for r in result.releases] == ["0.30.0", "0.29.0rc1", "0.28.1"]


# --------------------------------------------------------------------------
# Modelo y limite
# --------------------------------------------------------------------------


async def test_solo_se_devuelven_los_campos_de_nuestro_modelo(fake_github):
    """GitHub manda decenas de campos por release; publicamos diez."""
    crudo = {
        **MEZCLA[0],
        "node_id": "RE_kwDO",
        "assets": [{"name": "dist.whl", "size": 12345}],
        "tarball_url": "https://api.github.com/repos/encode/httpx/tarball/0.28.1",
        "zipball_url": "https://api.github.com/repos/encode/httpx/zipball/0.28.1",
        "upload_url": "https://uploads.github.com/...",
        "target_commitish": "master",
    }
    handler, _ = responde_releases([crudo])
    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert set(result.releases[0].model_dump()) == {
        "id",
        "tag_name",
        "name",
        "body",
        "draft",
        "prerelease",
        "created_at",
        "published_at",
        "author",
        "url",
    }


async def test_por_defecto_se_piden_diez_releases(fake_github):
    handler, parametros = responde_releases(MEZCLA)
    fake_github(handler)

    await github.analyze_repository("encode", "httpx")

    assert parametros[0]["per_page"] == "10"


async def test_el_limite_pedido_llega_a_github(fake_github):
    handler, parametros = responde_releases(MEZCLA)
    fake_github(handler)

    await github.analyze_repository("encode", "httpx", releases_limit=40)

    assert parametros[0]["per_page"] == "40"


async def test_limites_distintos_no_comparten_cache(fake_github):
    handler, parametros = responde_releases(MEZCLA)
    fake_github(handler)

    await github.analyze_repository("encode", "httpx", releases_limit=10)
    await github.analyze_repository("encode", "httpx", releases_limit=40)

    assert [p["per_page"] for p in parametros] == ["10", "40"]


async def test_el_mismo_limite_reutiliza_la_cache(fake_github):
    handler, _ = responde_releases(MEZCLA)
    fake_github(handler)

    primero = await github.analyze_repository("encode", "httpx", releases_limit=5)
    segundo = await github.analyze_repository("encode", "httpx", releases_limit=5)

    assert primero.cached is False
    assert segundo.cached is True


async def test_los_limites_anteriores_siguen_funcionando(fake_github):
    """Anadir #releases a la clave no debe romper los tres limites previos."""
    handler, parametros = responde_releases(MEZCLA)
    fake_github(handler)

    await github.analyze_repository(
        "encode", "httpx", commits_limit=5, issues_limit=7, pulls_limit=3
    )
    segundo = await github.analyze_repository(
        "encode", "httpx", commits_limit=5, issues_limit=7, pulls_limit=3
    )

    assert len(parametros) == 1, "el segundo analisis sale de la cache"
    assert segundo.cached is True


# --------------------------------------------------------------------------
# Integracion por HTTP
# --------------------------------------------------------------------------


def test_integracion_con_el_endpoint_analyze(fake_github):
    handler, _ = responde_releases(MEZCLA)
    fake_github(handler)

    response = TestClient(app).get("/analyze/encode/httpx")

    assert response.status_code == 200
    body = response.json()
    assert body["releases_count"] == 3
    assert body["published_releases_count"] == 2
    assert body["draft_releases_count"] == 1
    assert body["prereleases_count"] == 1
    assert body["releases"][0] == {
        "id": 300,
        "tag_name": "0.28.1",
        "name": "Version 0.28.1",
        "body": "Notas de la version",
        "draft": False,
        "prerelease": False,
        "created_at": "2024-12-06T15:00:00Z",
        "published_at": "2024-12-06T15:36:24Z",
        "author": "tomchristie",
        "url": "https://github.com/encode/httpx/releases/tag/0.28.1",
    }


def test_integracion_el_borrador_llega_con_published_at_null(fake_github):
    handler, _ = responde_releases(MEZCLA)
    fake_github(handler)

    body = TestClient(app).get("/analyze/encode/httpx").json()

    borrador = body["releases"][2]
    assert borrador["draft"] is True
    assert borrador["published_at"] is None
    assert borrador["name"] is None


def test_integracion_el_parametro_releases_llega_a_github(fake_github):
    handler, parametros = responde_releases(MEZCLA)
    fake_github(handler)

    response = TestClient(app).get("/analyze/encode/httpx?releases=3")

    assert response.status_code == 200
    assert parametros[0]["per_page"] == "3"


@pytest.mark.parametrize("valor", [0, -1, 101, 5000])
def test_integracion_cantidades_fuera_de_rango_devuelven_422(fake_github, valor):
    handler, parametros = responde_releases(MEZCLA)
    fake_github(handler)

    response = TestClient(app).get(f"/analyze/encode/httpx?releases={valor}")

    assert response.status_code == 422
    assert parametros == [], "no se llega a consultar GitHub"


def test_integracion_latest_release_sigue_funcionando(fake_github):
    """La lista nueva no sustituye a `latest_release`: son endpoints distintos."""
    handler, _ = responde_releases(MEZCLA)
    fake_github(handler)

    body = TestClient(app).get("/analyze/encode/httpx").json()

    assert body["latest_release"] == {
        "tag": "0.28.1",
        "name": "Version 0.28.1",
        "published_at": "2024-12-06T15:36:24Z",
        "url": "https://github.com/encode/httpx/releases/tag/0.28.1",
    }
    assert body["releases_count"] == 3, "y la lista completa sigue ahi"


def test_integracion_las_funcionalidades_anteriores_siguen_ahi(fake_github):
    """Releases no debe haber desplazado nada de lo que ya devolviamos."""
    handler, _ = responde_releases(MEZCLA)
    fake_github(handler)

    body = TestClient(app).get("/analyze/encode/httpx").json()

    assert body["repository"]["full_name"] == "encode/httpx"
    assert body["languages"] == {"Python": 570031, "Shell": 2821}
    assert body["contributors_count"] == 2
    assert len(body["recent_commits"]) == 1
    assert body["issues_count"] == 2
    assert body["pull_requests_count"] == 3
    assert body["merged_pull_requests_count"] == 1
