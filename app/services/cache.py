"""Cache en memoria con expiracion por tiempo (TTL).

Guarda valores durante un numero limitado de segundos. Sirve para no repetir
peticiones identicas a GitHub y agotar la cuota de la API.

Los datos viven en el proceso: al reiniciar el servidor la cache se vacia.
Es lo adecuado para un MVP; una cache compartida entre varios procesos
requeriria algo externo como Redis.
"""

import time
from collections import OrderedDict
from collections.abc import Callable


class TTLCache[T]:
    """Cache de tamano limitado en la que cada entrada caduca sola.

    Args:
        ttl_seconds: segundos que vive cada entrada. Con 0 o menos, la cache
            queda desactivada y nunca devuelve nada.
        max_size: numero maximo de entradas. Al superarlo se descarta la
            usada hace mas tiempo (politica LRU).
        clock: fuente de tiempo. Se puede sustituir en los tests para simular
            el paso del tiempo sin esperas reales.
    """

    def __init__(
        self,
        ttl_seconds: float,
        max_size: int = 128,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._ttl = ttl_seconds
        self._max_size = max_size
        self._clock = clock
        # clave -> (instante de caducidad, valor)
        self._entries: OrderedDict[str, tuple[float, T]] = OrderedDict()

    @property
    def enabled(self) -> bool:
        return self._ttl > 0

    def get(self, key: str) -> T | None:
        """Devuelve el valor guardado, o None si no existe o ha caducado."""
        if not self.enabled:
            return None

        entry = self._entries.get(key)
        if entry is None:
            return None

        expires_at, value = entry
        if self._clock() >= expires_at:
            del self._entries[key]
            return None

        # Marcar como recien usada para que no sea la primera en descartarse.
        self._entries.move_to_end(key)
        return value

    def set(self, key: str, value: T) -> None:
        """Guarda un valor, descartando el mas antiguo si no hay sitio."""
        if not self.enabled:
            return

        self._entries[key] = (self._clock() + self._ttl, value)
        self._entries.move_to_end(key)

        while len(self._entries) > self._max_size:
            self._entries.popitem(last=False)

    def clear(self) -> None:
        self._entries.clear()

    def __len__(self) -> int:
        return len(self._entries)
