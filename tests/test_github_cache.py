"""Tests de la cache aplicada al servicio: cuantas veces se llama a GitHub."""

import httpx

from app.schemas.repository import AnalysisResponse
from app.services import github
from app.services.cache import TTLCache
from tests.conftest import successful_handler


def counting_handler() -> tuple[list[str], callable]:
    """Manejador que ademas anota cada ruta pedida a GitHub."""
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        return successful_handler(request)

    return calls, handler


async def test_la_segunda_peticion_no_llama_a_github(fake_github):
    calls, handler = counting_handler()
    fake_github(handler)

    first = await github.analyze_repository("encode", "httpx")
    second = await github.analyze_repository("encode", "httpx")

    assert len(calls) == 5, "el primer analisis usa los 5 endpoints de GitHub"
    assert first.cached is False
    assert second.cached is True
    assert second.repository == first.repository


async def test_repositorios_distintos_no_comparten_cache(fake_github):
    calls, handler = counting_handler()
    fake_github(handler)

    await github.analyze_repository("encode", "httpx")
    await github.analyze_repository("fastapi", "fastapi")

    assert len(calls) == 10


async def test_la_clave_ignora_mayusculas(fake_github):
    """GitHub trata ENCODE/HTTPX y encode/httpx como el mismo repositorio."""
    calls, handler = counting_handler()
    fake_github(handler)

    await github.analyze_repository("encode", "httpx")
    result = await github.analyze_repository("ENCODE", "HTTPX")

    assert len(calls) == 5
    assert result.cached is True


async def test_al_caducar_se_vuelve_a_consultar_github(fake_github, monkeypatch):
    calls, handler = counting_handler()
    fake_github(handler)

    # Cambiamos la cache del modulo por una con reloj controlado por el test.
    now = [0.0]
    monkeypatch.setattr(
        github,
        "_cache",
        TTLCache[AnalysisResponse](ttl_seconds=60, clock=lambda: now[0]),
    )

    await github.analyze_repository("encode", "httpx")
    now[0] = 61.0
    result = await github.analyze_repository("encode", "httpx")

    assert len(calls) == 10, "tras caducar se vuelve a preguntar a GitHub"
    assert result.cached is False


async def test_un_error_no_se_guarda_en_cache(fake_github):
    """Solo cacheamos exitos: un fallo puntual no debe quedarse pegado."""
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        return httpx.Response(404, json={"message": "Not Found"})

    fake_github(handler)

    for _ in range(2):
        try:
            await github.analyze_repository("SantiDev11", "no-existe")
        except github.RepositoryNotFound:
            pass

    assert len(calls) > 5, "el segundo intento vuelve a preguntar a GitHub"
