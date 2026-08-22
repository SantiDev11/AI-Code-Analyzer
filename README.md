# AI-Code-Analyzer

Backend en FastAPI que realiza un análisis técnico integral de repositorios públicos de GitHub combinando datos de la GitHub REST API, señales de calidad de código, métricas cuantitativas y un análisis técnico estructurado generado por Inteligencia Artificial.

---

## Características Principales

1. **Repository Metadata & Stats:** Métricas generales, estrellas, forks, lenguaje predominante, licencia, topics y tamaño.
2. **Languages & Contributors:** Distribución de bytes por lenguaje y principales colaboradores.
3. **Recent Commits, Issues & Pull Requests:** Muestreo reciente con conteos clasificados (abiertos, cerrados, mergeados).
4. **Releases & Versioning:** Historial reciente de versiones diferenciando publicaciones, borradores y prereleases.
5. **Activity (Días Naturales UTC):** Distribución temporal diaria de actividad sin peticiones extra a la API.
6. **Code Quality Signals:** Detección de configuración de tests, documentación (README, CONTRIBUTING, docs/), CI/CD, linters, formateadores, tipado estático y cobertura a partir del Git Tree de la rama por defecto.
7. **Code Metrics:** Recuento de archivos, directorios jerárquicos, clasificación (source, test, doc, config), distribución por extensión y top de archivos más pesados.
8. **AI Technical Analysis:** Evaluación técnica fundamentada estrictamente en evidencia real (resumen, fortalezas, aspectos de atención con evidencia, recomendaciones accionables y visión técnica).

---

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/analyze/{owner}/{repo}` | Analiza un repositorio público |
| `GET` | `/analyze/{owner}/{repo}?commits=N` | Cantidad de commits recientes a incluir (1–100, def: 10) |
| `GET` | `/analyze/{owner}/{repo}?issues=N` | Cantidad de issues a analizar (1–100, def: 10) |
| `GET` | `/analyze/{owner}/{repo}?pulls=N` | Cantidad de pull requests a analizar (1–100, def: 10) |
| `GET` | `/analyze/{owner}/{repo}?releases=N` | Cantidad de releases a analizar (1–100, def: 10) |
| `GET` | `/analyze/{owner}/{repo}?activity_days=N` | Ventana en días para el análisis de actividad (1–365, def: 30) |
| `GET` | `/health` | Healthcheck del servicio |
| `GET` | `/docs` | Documentación interactiva Swagger UI |
| `GET` | `/redoc` | Documentación interactiva ReDoc |

---

## Ejemplo de Uso

```bash
curl http://127.0.0.1:8000/analyze/encode/httpx
```

### Respuesta de Ejemplo

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
    "is_archived": false,
    "default_branch": "master"
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
      "url": "https://github.com/encode/httpx/commit/b5addb6"
    }
  ],
  "issues": [],
  "issues_count": 0,
  "open_issues_count": 0,
  "closed_issues_count": 0,
  "pull_requests": [],
  "pull_requests_count": 0,
  "open_pull_requests_count": 0,
  "closed_pull_requests_count": 0,
  "merged_pull_requests_count": 0,
  "releases": [],
  "releases_count": 0,
  "published_releases_count": 0,
  "draft_releases_count": 0,
  "prereleases_count": 0,
  "activity": {
    "days": 30,
    "since": "2026-07-23",
    "until": "2026-08-22",
    "total_commits": 1,
    "total_issues": 0,
    "total_pull_requests": 0,
    "total_releases": 0,
    "daily": [
      {
        "date": "2026-02-23",
        "commits": 1,
        "issues": 0,
        "pull_requests_opened": 0,
        "pull_requests_closed": 0,
        "releases": 0
      }
    ]
  },
  "quality": {
    "tree_available": True,
    "tree_truncated": False,
    "files_scanned": 150,
    "tests": {
      "detected": True,
      "files": 12,
      "directories": ["tests"]
    },
    "documentation": {
      "readme": True,
      "contributing": True,
      "docs_directory": True,
      "files": ["README.md", "CONTRIBUTING.md"]
    },
    "ci": {
      "detected": True,
      "files": [".github/workflows/test.yml"]
    },
    "linting": {
      "detected": True,
      "files": [".flake8"]
    },
    "formatting": {
      "detected": True,
      "files": [".editorconfig"]
    },
    "type_checking": {
      "detected": True,
      "files": ["mypy.ini"]
    },
    "dependencies": {
      "detected": True,
      "files": ["pyproject.toml"]
    },
    "coverage": {
      "configured": True,
      "percentage": null,
      "files": [".coveragerc"]
    },
    "undetermined_config": ["pyproject.toml"]
  },
  "metrics": {
    "tree_available": True,
    "tree_truncated": False,
    "total_files": 150,
    "total_directories": 24,
    "source_files": 110,
    "test_files": 12,
    "documentation_files": 5,
    "configuration_files": 8,
    "file_extensions": {
      ".py": 122,
      ".md": 5,
      ".toml": 2,
      ".yml": 2
    },
    "largest_files": [
      {
        "path": "httpx/_client.py",
        "size_bytes": 48200
      }
    ],
    "lines_of_code": null
  },
  "ai_analysis": {
    "summary": "HTTPX es una libreria HTTP moderna, modular y con solida ingenieria de software.",
    "strengths": [
      "Suite de pruebas exhaustivo con cobertura amplia en modo sincrono y asincrono.",
      "Flujo de integracion continua y tipado estricto con mypy implementados."
    ],
    "concerns": [
      {
        "title": "Configuracion de cobertura no verificable en raiz",
        "description": "No se detecto reporte publico de porcentaje de cobertura.",
        "severity": "low",
        "evidence": "CoverageSignal porcentaje es null en los metadatos."
      }
    ],
    "recommendations": [
      {
        "title": "Publicar insignias de cobertura en README",
        "description": "Vincular el servicio de Codecov para visibilidad publica del estado de los tests.",
        "priority": "low"
      }
    ],
    "technical_overview": {
      "architecture": "Cliente HTTP modular con soporte para backends anyio, trio y asyncio.",
      "stack": "Python, httpx, mypy, pytest, ruff, GitHub Actions.",
      "activity_summary": "Proyecto estable con mantenimiento continuo y versiones publicadas periodicamente."
    }
  },
  "cached": False
}
```

---

## Configuración y Variables de Entorno

Copia el archivo `.env.example` como `.env`:

```bash
cp .env.example .env
```

### Parámetros Disponibles:

```ini
# Token personal de GitHub (opcional pero recomendado para elevar el rate limit de 60 a 5000 peticiones/hora)
GITHUB_TOKEN=

# Tiempo de vida de la cache en memoria en segundos (0 para desactivar)
CACHE_TTL_SECONDS=300

# Dias naturales por defecto para el analisis de actividad
ACTIVITY_DAYS=30

# Configuracion de Inteligencia Artificial (OpenAI-compatible)
AI_PROVIDER=openai
AI_API_KEY=
AI_MODEL=gpt-4o-mini
AI_BASE_URL=https://api.openai.com/v1
AI_TIMEOUT_SECONDS=30.0
```

> **Comportamiento sin IA:** Si `AI_API_KEY` no se define o está vacía, el análisis de GitHub funciona con total normalidad y `ai_analysis` devuelve `null` de forma segura.

---

## Instalación y Ejecución

Requiere **Python 3.12+**.

```bash
# 1. Crear y activar entorno virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Iniciar servidor de desarrollo
uvicorn app.main:app --reload
```

Accede a <http://127.0.0.1:8000/docs> para explorar y probar la API en Swagger UI.

---

## Ejecución de Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Todas las pruebas utilizan transportes simulados (`httpx.MockTransport`): no consumen cuota de la GitHub API ni realizan peticiones reales al proveedor de IA.

---

## Arquitectura Interna

```
Cliente HTTP (Swagger / Frontend / cURL)
                     ↓
             app/api/routes.py
                     ↓
        app/services/github.py (Orquestador de llamadas en paralelo)
       ├── GitHub REST API (8 endpoints paralelos)
       ├── Git Tree de default_branch (1 única llamada para Quality + Metrics)
       ├── app/services/quality.py (Deducción de señales en memoria)
       ├── app/services/metrics.py (Cálculo de métricas en memoria)
       ├── app/services/ai/service.py (Análisis técnico con IA)
       │    ├── Context Builder (Límites seguros sin secretos)
       │    ├── AI Client (HTTP OpenAI-compatible)
       │    └── Pydantic Schema Validation (AIAnalysis)
       └── app/services/cache.py (Caché en memoria con TTL)
```

---

## Limitaciones Conocidas

1. **Líneas de Código (`lines_of_code = null`):** La API de Git Tree proporciona tamaños en bytes (`size`), pero no contenidos. Para no saturar la cuota ni descargar repositorios completos, `lines_of_code` se mantiene como `null` explícito.
2. **Git Tree Truncado (`tree_truncated = True`):** En repositorios masivos (> 100,000 archivos), GitHub trunca el árbol. El sistema marca `tree_truncated: true` y evalúa únicamente sobre el subconjunto recibido sin asumir falsos negativos.
3. **Señales de Calidad Nulas:** Si el árbol de archivos no está disponible o fue truncado, las señales de calidad se marcan como `null` en lugar de `false`.
4. **Disponibilidad de IA:** `ai_analysis` depende de la conectividad y cuota del proveedor externo configurado. Ante errores del proveedor, rate limits o respuestas malformadas, el sistema degrada elegantemente devolviendo `ai_analysis: null` sin afectar la respuesta general.
5. **Aislamiento y Seguridad:** El backend **nunca** ejecuta archivos, scripts, `Makefile`, `package.json` ni dependencias del repositorio analizado.
