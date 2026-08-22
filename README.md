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
    "url": "https://github.com/encode/httpx"
  },
  "languages": {
    "Python": 570031,
    "Shell": 2821
  },
  "contributors_count": 247
}
```

Los campos `description`, `primary_language` y `contributors_count` pueden ser
`null`. Significa que GitHub no proporciona ese dato para ese repositorio; nunca
se sustituye por un valor inventado.

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
3 peticiones, son unos **20 analisis/hora**. Con un token se sube a 5000/hora.

1. Crea un token en <https://github.com/settings/tokens> **sin marcar ningun
   scope** (solo necesitamos leer datos publicos).
2. Copia `.env.example` como `.env` y pega el token:

```
GITHUB_TOKEN=ghp_tu_token_aqui
```

El archivo `.env` esta en `.gitignore` y nunca se sube al repositorio.

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
│   │   └── github.py           # Comunicacion con la GitHub REST API
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

Un analisis necesita tres endpoints distintos de GitHub, que se consultan **en
paralelo** con `asyncio.gather`:

| Dato | Endpoint de GitHub |
|---|---|
| Datos generales | `GET /repos/{owner}/{repo}` |
| Lenguajes | `GET /repos/{owner}/{repo}/languages` |
| Numero de contributors | `GET /repos/{owner}/{repo}/contributors?per_page=1` |

Para contar contributors no se recorren todas las paginas: se pide **un
contributor por pagina** y se lee el numero de la ultima pagina de la cabecera
`Link`, con lo que basta una sola peticion.
