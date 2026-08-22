"""Tests de la cache TTL. Usan un reloj falso: no hay esperas reales."""

import pytest

from app.services.cache import TTLCache


@pytest.fixture
def clock():
    """Reloj manipulable: clock.now avanza cuando el test lo decide."""

    class FakeClock:
        now = 0.0

        def __call__(self) -> float:
            return self.now

    return FakeClock()


def test_guarda_y_devuelve_un_valor(clock):
    cache = TTLCache[str](ttl_seconds=10, clock=clock)

    cache.set("clave", "valor")

    assert cache.get("clave") == "valor"


def test_clave_inexistente_devuelve_none(clock):
    cache = TTLCache[str](ttl_seconds=10, clock=clock)

    assert cache.get("no-existe") is None


def test_el_valor_caduca_al_cumplirse_el_ttl(clock):
    cache = TTLCache[str](ttl_seconds=10, clock=clock)
    cache.set("clave", "valor")

    clock.now = 9.9
    assert cache.get("clave") == "valor"

    clock.now = 10.0
    assert cache.get("clave") is None


def test_la_entrada_caducada_se_elimina(clock):
    """No basta con no devolverla: hay que liberar la memoria."""
    cache = TTLCache[str](ttl_seconds=10, clock=clock)
    cache.set("clave", "valor")

    clock.now = 20.0
    cache.get("clave")

    assert len(cache) == 0


def test_ttl_cero_desactiva_la_cache(clock):
    cache = TTLCache[str](ttl_seconds=0, clock=clock)

    cache.set("clave", "valor")

    assert cache.enabled is False
    assert cache.get("clave") is None
    assert len(cache) == 0


def test_al_llenarse_descarta_la_entrada_menos_usada(clock):
    cache = TTLCache[str](ttl_seconds=100, max_size=2, clock=clock)
    cache.set("a", "1")
    cache.set("b", "2")

    # Al leer "a" pasa a ser la mas reciente, asi que "b" queda como candidata.
    cache.get("a")
    cache.set("c", "3")

    assert len(cache) == 2
    assert cache.get("a") == "1"
    assert cache.get("c") == "3"
    assert cache.get("b") is None


def test_clear_vacia_la_cache(clock):
    cache = TTLCache[str](ttl_seconds=10, clock=clock)
    cache.set("a", "1")
    cache.set("b", "2")

    cache.clear()

    assert len(cache) == 0
