# AI-Code-Analyzer

Backend en FastAPI que consulta datos reales de repositorios publicos de GitHub
a traves de la GitHub REST API.

> Version actual: **MVP**. Sin inteligencia artificial, frontend, base de datos
> ni Docker. Solo el backend y un endpoint.

## Endpoints

| Metodo | Ruta | Descripcion |
|---|---|---|
| `GET` | `/analyze/{owner}/{repo}` | Analiza un repositorio publico |
| `GET` | `/analyze/{owner}/{repo}?commits=N` | Igual, pidiendo N commits recientes |
| `GET` | `/analyze/{owner}/{repo}?issues=N` | Igual, analizando N issues |
| `GET` | `/analyze/{owner}/{repo}?pulls=N` | Igual, analizando N pull requests |
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
    "full_name": "encode/httpx",
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
  "contributors": [
    {
      "username": "tomchristie",
      "contributions": 1042,
      "avatar_url": "https://avatars.githubusercontent.com/u/647359",
      "profile_url": "https://github.com/tomchristie"
    }
  ],
  "contributors_count": 1,
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

Los campos `description`, `primary_language`, `license` y
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
6 peticiones, son solo **10 analisis/hora**. Con un token se sube a 5000/hora,
es decir unos 830 analisis. Se recomienda configurarlo.

1. Crea un token en <https://github.com/settings/tokens> **sin marcar ningun
   scope** (solo necesitamos leer datos publicos).
2. Copia `.env.example` como `.env` y pega el token:

```
GITHUB_TOKEN=ghp_tu_token_aqui
```

El archivo `.env` esta en `.gitignore` y nunca se sube al repositorio.

## Cache

Cada analisis consume 6 peticiones de la cuota de GitHub, asi que los
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

Un analisis necesita siete endpoints distintos de GitHub, que se consultan **en
paralelo** con `asyncio.gather`:

| Dato | Endpoint de GitHub |
|---|---|
| Datos generales, licencia, topics, tamano | `GET /repos/{owner}/{repo}` |
| Lenguajes | `GET /repos/{owner}/{repo}/languages` |
| Contributors | `GET /repos/{owner}/{repo}/contributors?per_page=10` |
| Ultima release | `GET /repos/{owner}/{repo}/releases/latest` |
| Commits recientes | `GET /repos/{owner}/{repo}/commits?per_page=10` |
| Issues | `GET /repos/{owner}/{repo}/issues?per_page=10&state=all` |
| Pull requests | `GET /repos/{owner}/{repo}/pulls?per_page=10&state=all&sort=created&direction=desc` |

De issues se analizan **10** por defecto, ajustables con `issues` (1-100).
GitHub sirve los pull requests por el mismo endpoint que los issues, asi que se
descartan mirando la clave `pull_request`, que solo ellos llevan. Los tres
contadores (`issues_count`, `open_issues_count`, `closed_issues_count`) se
calculan despues de ese filtro, sobre los issues que de verdad analizamos.

Cuidado con no confundir `repository.open_issues`, que es el contador de GitHub
e **incluye pull requests**, con `open_issues_count`, que cuenta solo issues
reales de la muestra analizada.

De pull requests se analizan **10** por defecto, ajustables con `pulls`
(1-100). Se piden a `/pulls` y no a `/issues` porque solo ese endpoint trae la
fecha de merge y las ramas de origen y destino.

Ojo con los contadores, porque GitHub solo tiene dos estados (`open` y
`closed`) y el merge es otra cosa distinta:

| Contador | Como se calcula |
|---|---|
| `open_pull_requests_count` | `state == "open"` |
| `closed_pull_requests_count` | `state == "closed"`, **mergeados incluidos** |
| `merged_pull_requests_count` | `merged_at` tiene fecha |

Un pull request mergeado esta cerrado, asi que suma en los dos ultimos a la
vez: `merged` no es un tercer estado, sino algo que le pasa a uno cerrado. El
campo `merged` de GitHub no sirve aqui, porque solo aparece al pedir un pull
request de uno en uno; en el listado el unico rastro del merge es `merged_at`.

De commits recientes se devuelven **10** por defecto. La cantidad se ajusta con
el parametro `commits` (entre 1 y 100, el maximo que sirve GitHub por pagina);
fuera de ese rango la API responde `422`. El limite forma parte de la clave de
cache, asi que pedir una cantidad distinta vuelve a consultar a GitHub.

De contributors se publican los mas activos, no la lista entera: GitHub ya los
devuelve ordenados de mas a menos contribuciones, asi que basta la primera
pagina. `contributors_count` describe cuantos incluye esa lista.

Algunos codigos de GitHub no son errores segun el endpoint:

| Endpoint | Codigo | Significado real | Se devuelve |
|---|---|---|---|
| `/releases/latest` | 404 | El repositorio no tiene releases | `null` |
| `/commits` | 409 | El repositorio esta vacio | `[]` |
| `/issues` | 404 | El repositorio tiene los issues desactivados | `[]` |
| `/contributors` | 204 | El repositorio esta vacio | `0` |
| `/contributors` | 403 | Historial demasiado grande para listarlo | `[]` |

Por eso cada uno se trata por separado antes de la comprobacion general de
errores: un 404 en `/releases/latest` no significa que el repositorio no exista.
