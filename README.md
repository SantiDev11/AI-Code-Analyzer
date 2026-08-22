# AI-Code-Analyzer

Backend en FastAPI que consulta datos reales de repositorios publicos de GitHub
a traves de la GitHub REST API.

> Version actual: **MVP**. Sin inteligencia artificial, frontend, base de datos
> ni Docker. Solo el backend y un endpoint.

## Endpoints

| Metodo | Ruta | Descripcion |
|---|---|---|
| `GET` | `/analyze/{owner}/{repo}` | Analiza un repositorio publico |
| `GET` | `/health` | Comprueba que el servicio esta vivo |
| `GET` | `/docs` | Documentacion interactiva (Swagger UI) |

### Ejemplo

```bash
curl http://127.0.0.1:8000/analyze/encode/httpx
```

```json
{
  "repository": {
    "name": "httpx",
    "description": "A next generation HTTP client for Python.",
    "stars": 15429,
    "forks": 1256,
    "open_issues": 143,
    "created_at": "2019-04-04T12:27:00Z",
    "updated_at": "2026-08-22T15:17:06Z",
    "primary_language": "Python",
    "url": "https://github.com/encode/httpx",
    "license": "BSD-3-Clause",
    "topics": ["asyncio", "http", "python", "trio"],
    "size_kb": 8594,
    "is_archived": false
  },
  "languages": {
    "Python": 570031,
    "Shell": 2821
  },
  "contributors_count": 247,
  "latest_release": {
    "tag": "0.28.1",
    "name": "Version 0.28.1",
    "published_at": "2024-12-06T15:36:24Z",
    "url": "https://github.com/encode/httpx/releases/tag/0.28.1"
  },
  "recent_commits": [
    {
      "sha": "b5addb6",
      "message": "Adapt test_response_decode_text_using_autodetect for chardet 6.0",
      "author": "musicinmybrain",
      "date": "2026-02-23T10:40:42Z",
      "url": "https://github.com/encode/httpx/commit/b5addb6..."
    }
  ],
  "cached": false
}
```

Los campos `description`, `primary_language`, `license`, `contributors_count` y
`latest_release` pueden ser `null`. Significa que GitHub no proporciona ese dato
para ese repositorio; nunca se sustituye por un valor inventado.

### Codigos de error

| Codigo | Cuando ocurre |
|---|---|
| `404` | El repositorio no existe o es privado |
| `429` | Cuota de la GitHub API agotada |
| `502` | GitHub ha respondido algo inesperado |
| `503` | GitHub no responde (timeout o fallo de red) |

## Instalacion

Requiere **Python 3.12+**.

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS

pip install -r requirements.txt
```

## Token de GitHub (opcional)

Sin token la API permite **60 peticiones/hora** por IP. Como cada analisis hace
5 peticiones, son solo **12 analisis/hora**. Con un token se sube a 5000/hora,
es decir unos 1000 analisis. Se recomienda configurarlo.

1. Crea un token en <https://github.com/settings/tokens> **sin marcar ningun
   scope** (solo necesitamos leer datos publicos).
2. Copia `.env.example` como `.env` y pega el token:

```
GITHUB_TOKEN=ghp_tu_token_aqui
```

El archivo `.env` esta en `.gitignore` y nunca se sube al repositorio.

## Cache

Cada analisis consume 5 peticiones de la cuota de GitHub, asi que los
resultados se guardan en memoria durante 5 minutos por defecto. Una segunda
consulta al mismo repositorio se responde al instante y sin gastar cuota:

```
GET /analyze/encode/httpx   ->  6242 ms   "cached": false
GET /analyze/encode/httpx   ->     0 ms   "cached": true
```

El campo `cached` de la respuesta indica el origen de los datos. El tiempo de
vida se ajusta con `CACHE_TTL_SECONDS` en el `.env`; con `0` se desactiva.

La cache vive dentro del proceso: al reiniciar el servidor se vacia, y cada
proceso tiene la suya. Es suficiente para un MVP; compartirla entre varios
procesos exigiria algo externo como Redis.

## Ejecucion

```bash
uvicorn app.main:app --reload
```

Abre <http://127.0.0.1:8000/docs> para probar el endpoint desde el navegador.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Los tests simulan las respuestas de GitHub con `httpx.MockTransport`: no
necesitan conexion a internet ni consumen cuota de la API.

## Estructura

```
AI-Code-Analyzer/
├── app/
│   ├── main.py                 # Punto de entrada: crea la app y monta el router
│   ├── config.py               # Lee GITHUB_TOKEN del entorno o del .env
│   ├── api/
│   │   └── routes.py           # Endpoints y traduccion de errores a codigos HTTP
│   ├── services/
│   │   ├── github.py           # Comunicacion con la GitHub REST API
│   │   └── cache.py            # Cache en memoria con expiracion (TTL)
│   └── schemas/
│       └── repository.py       # Modelos Pydantic: el contrato de la respuesta
├── tests/
├── .env.example
├── requirements.txt
├── requirements-dev.txt
└── pytest.ini
```

Cada capa depende solo de la siguiente: `routes` no sabe hablar con GitHub y
`github.py` no sabe nada de FastAPI. Eso permite testear el servicio de forma
aislada y cambiar una capa sin tocar las demas.

## Como funciona por dentro

Un analisis necesita cinco endpoints distintos de GitHub, que se consultan **en
paralelo** con `asyncio.gather`:

| Dato | Endpoint de GitHub |
|---|---|
| Datos generales, licencia, topics, tamano | `GET /repos/{owner}/{repo}` |
| Lenguajes | `GET /repos/{owner}/{repo}/languages` |
| Numero de contributors | `GET /repos/{owner}/{repo}/contributors?per_page=1` |
| Ultima release | `GET /repos/{owner}/{repo}/releases/latest` |
| Commits recientes | `GET /repos/{owner}/{repo}/commits?per_page=5` |

Para contar contributors no se recorren todas las paginas: se pide **un
contributor por pagina** y se lee el numero de la ultima pagina de la cabecera
`Link`, con lo que basta una sola peticion.

Algunos codigos de GitHub no son errores segun el endpoint:

| Endpoint | Codigo | Significado real | Se devuelve |
|---|---|---|---|
| `/releases/latest` | 404 | El repositorio no tiene releases | `null` |
| `/commits` | 409 | El repositorio esta vacio | `[]` |
| `/contributors` | 204 | El repositorio esta vacio | `0` |
| `/contributors` | 403 | Historial demasiado grande para contarlo | `null` |

Por eso cada uno se trata por separado antes de la comprobacion general de
errores: un 404 en `/releases/latest` no significa que el repositorio no exista.
