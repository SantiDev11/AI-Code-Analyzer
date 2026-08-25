# AI-Code-Analyzer

[![CI](https://github.com/SantiDev11/AI-Code-Analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/SantiDev11/AI-Code-Analyzer/actions/workflows/ci.yml)

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

# Origenes permitidos por CORS, separados por comas y sin espacios. Nunca se usa "*"
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173

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

### 1. Backend (FastAPI)

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

### 2. Frontend (React + TypeScript + Vite)

Requiere **Node.js 18+** y **npm**.

```bash
# 1. Navegar al directorio frontend e instalar dependencias
cd frontend
npm install

# 2. Configurar variables de entorno (opcional)
# Por defecto el proxy de Vite redirige las llamadas locales a http://localhost:8000,
# así que VITE_API_BASE_URL puede quedarse vacía.
cp .env.example .env
# Solo si el backend vive en otro dominio, con su URL pública y accesible
# desde el navegador. El valor se incrusta en el bundle: nunca pongas secretos.
# VITE_API_BASE_URL=https://api.example.com

# 3. Iniciar servidor de desarrollo frontend
npm run dev

# 4. Compilar bundle de producción
npm run build

# 5. Comprobación estricta de tipos
npm run typecheck
```

Accede a <http://localhost:3000> para interactuar con la interfaz del analizador.

---

## Ejecución con Docker

Empaqueta el proyecto completo (backend + frontend) sin instalar Python ni Node en la máquina.

### Prerequisitos

- **Docker Engine 24+** con el plugin **Docker Compose v2** (`docker compose`, no `docker-compose`).
- Docker Desktop en marcha si estás en Windows o macOS.

### Arquitectura

Dos imágenes independientes coordinadas por `compose.yaml`:

| Servicio   | Imagen base                       | Puerto interno | Puerto publicado |
| ---------- | --------------------------------- | -------------- | ---------------- |
| `backend`  | `python:3.12-slim` + Uvicorn      | 8000           | `8000`           |
| `frontend` | `nginx-unprivileged` (multi-stage) | 8080           | `3000`           |

El frontend se compila con Node en una etapa de build y el bundle estático resultante lo sirve nginx. El servidor de desarrollo de Vite **no** se usa en runtime.

El navegador solo habla con `http://localhost:3000`. Las llamadas a `/analyze/...` y `/health` salen relativas a ese mismo origen y nginx las reenvía al contenedor `backend` por la red interna de Docker:

```
Navegador ──► localhost:3000 (nginx) ──► backend:8000 (red interna)
```

El hostname `backend` solo lo resuelve nginx dentro de la red de Compose; el navegador nunca lo necesita.

### Comandos

```bash
# Construir las imágenes
docker compose build

# Levantar (en primer plano, con logs)
docker compose up

# Construir y levantar en un solo paso
docker compose up --build

# Levantar en segundo plano
docker compose up -d

# Ver el estado y los healthchecks
docker compose ps

# Detener y eliminar los contenedores
docker compose down
```

### URLs

| Recurso            | URL                             |
| ------------------ | ------------------------------- |
| Frontend           | <http://localhost:3000>         |
| Backend (API)      | <http://localhost:8000>         |
| Swagger UI         | <http://localhost:8000/docs>    |
| Health check       | <http://localhost:8000/health>  |

`/health` también es accesible desde el origen del frontend en <http://localhost:3000/health>, ya que nginx hace de proxy. Es el mismo endpoint que usa el `healthcheck` del contenedor: el `frontend` no arranca hasta que el `backend` responde sano.

### Variables de entorno

Compose lee el archivo `.env` de la raíz (ignorado por git) y **inyecta** sus valores como variables de entorno del contenedor. Ese archivo nunca se copia dentro de la imagen: `.dockerignore` lo excluye del contexto de build, así que ningún secreto queda en las capas ni en el historial de la imagen.

Todas las variables son opcionales; sin ninguna de ellas los contenedores arrancan igualmente y el análisis de GitHub funciona (con el rate limit anónimo y sin IA).

**Variables secretas — solo backend, nunca salen del contenedor:**

| Variable       | Descripción                                                      |
| -------------- | ---------------------------------------------------------------- |
| `GITHUB_TOKEN` | Token personal de GitHub. Eleva el rate limit de 60 a 5000 req/h. |
| `AI_API_KEY`   | Clave del proveedor de IA. Sin ella, `ai_analysis` devuelve `null`. |

**Variables de configuración — no sensibles, también solo backend:**

`AI_PROVIDER`, `AI_MODEL`, `AI_BASE_URL`, `AI_TIMEOUT_SECONDS`, `CACHE_TTL_SECONDS`, `ACTIVITY_DAYS`, `CORS_ALLOWED_ORIGINS`.

**Variables públicas — frontend:**

| Variable             | Descripción                                                                |
| -------------------- | -------------------------------------------------------------------------- |
| `VITE_API_BASE_URL`  | URL base del backend. Vacía por defecto: el bundle usa rutas relativas.     |

> ⚠️ **Las variables `VITE_*` no son secretas.** Vite las sustituye por su valor literal *durante el build*, quedando incrustadas en el JavaScript que descarga el navegador. Cualquiera puede leerlas abriendo las DevTools. Nunca pongas en una `VITE_*` un token, una clave de API ni ningún otro secreto: para eso están `GITHUB_TOKEN` y `AI_API_KEY`, que viven exclusivamente en el backend.

#### Cómo se resuelve `VITE_API_BASE_URL`

Se pasa como `build arg` al `frontend/Dockerfile`, porque el valor debe existir en el momento de compilar (cambiarlo exige reconstruir la imagen, no basta con reiniciar el contenedor).

- **Vacía (por defecto con Compose):** el cliente hace peticiones relativas (`/analyze/...`) y nginx las reenvía al backend. Mismo origen, sin CORS.
- **Con valor** (por ejemplo `https://api.midominio.com`): el navegador llama directamente a esa URL. Debe ser una URL **pública, alcanzable desde el navegador** — nunca `http://backend:8000`, que solo existe dentro de la red de Docker. En ese caso hay que añadir el origen del frontend a `CORS_ALLOWED_ORIGINS`.

### CORS

El backend configura los orígenes permitidos con `CORS_ALLOWED_ORIGINS` (lista separada por comas). **Nunca se usa `allow_origins=["*"]`**; los métodos se limitan a `GET` y `OPTIONS`.

Por defecto se permiten `http://localhost:3000` y `http://localhost:5173` (más sus variantes `127.0.0.1`), que cubren tanto el frontend de Docker como `npm run dev`.

Con la configuración estándar de Compose el navegador nunca hace peticiones cross-origin, porque nginx sirve la interfaz y la API bajo el mismo origen. CORS solo entra en juego en llamadas directas al puerto 8000 (Swagger UI, `curl`, `npm run dev`) o si publicas el backend en un dominio distinto, en cuyo caso basta con ajustar la variable:

```bash
CORS_ALLOWED_ORIGINS=https://midominio.com
```

### Notas de seguridad

- Ambos contenedores ejecutan como usuario **sin privilegios** (`appuser` uid 1000 en el backend; nginx unprivileged en el frontend).
- Ni `.env`, ni `.venv`, ni `node_modules` del host entran en el contexto de build (`.dockerignore` y `frontend/.dockerignore`).
- No hay ningún secreto escrito en los `Dockerfile` ni en `compose.yaml`: solo referencias `${VARIABLE}`.

---

## Ejecución de Tests

### Tests del Backend (pytest)

```bash
pip install -r requirements-dev.txt
pytest
```

Todas las pruebas del backend utilizan transportes simulados (`httpx.MockTransport`): no consumen cuota de la GitHub API ni realizan peticiones reales al proveedor de IA.

### Tests del Frontend (Vitest)

```bash
cd frontend
npm test
```

Las suites de pruebas del frontend renderizan los componentes de forma estática con datos mockeados y verifican accesibilidad semántica, ausencia de valores nulos o inválidos y gestión de estados.

---

## Integración Continua (CI)

El pipeline vive en [`.github/workflows/ci.yml`](.github/workflows/ci.yml) y se ejecuta en GitHub Actions.

### Cuándo se ejecuta

- En cada **push** a `main`.
- En cada **pull request** dirigida a `main`.

Un push nuevo sobre la misma referencia cancela la ejecución anterior que siga en curso (`concurrency`), para no acumular builds obsoletos.

### Qué ejecuta

Tres jobs. `backend` y `frontend` corren **en paralelo**; `docker` solo arranca si ambos han pasado, para no gastar minutos construyendo imágenes de un commit que ya se sabe roto.

| Job        | Runtime     | Pasos                                                        |
| ---------- | ----------- | ------------------------------------------------------------ |
| `backend`  | Python 3.12 | `pip install -r requirements-dev.txt` → `pytest`              |
| `frontend` | Node 22     | `npm ci` → `npm test` → `npm run typecheck` → `npm run build` |
| `docker`   | —           | `docker compose config` → `docker compose build`              |

Las versiones no son arbitrarias: **Python 3.12** es la de la imagen de producción (`Dockerfile`) y **Node 22** la de la etapa de build de `frontend/Dockerfile`. La CI valida lo que realmente se despliega.

El caché de dependencias se apoya en los lockfiles (`requirements*.txt` y `frontend/package-lock.json`): al cambiar cualquiera de ellos, la clave de caché cambia y se reinstala desde cero.

### Qué hace fallar el pipeline

| Job        | Condición de fallo                                                                   |
| ---------- | ------------------------------------------------------------------------------------ |
| `backend`  | Cualquier test de `pytest` que falle, o un error instalando dependencias.             |
| `frontend` | Un test de Vitest en rojo, un error de tipos en `tsc`, o un fallo de `vite build`.    |
| `docker`   | `compose.yaml` inválido, o que alguna de las dos imágenes no construya.               |

`npm run build` ejecuta `tsc && vite build`, así que un error de tipos también rompe el build además del paso de `typecheck`.

### Secretos

**La CI no necesita ningún secreto.** No se declaran `GITHUB_TOKEN` ni `AI_API_KEY` en el workflow: los tests del backend sustituyen el cliente HTTP por transportes simulados (`tests/conftest.py`), de modo que **no se llama a la GitHub API ni a ningún proveedor de IA** durante la ejecución.

El job de `docker` solo construye las imágenes; **no publica nada** en ningún registro.

Los permisos del token automático están reducidos al mínimo:

```yaml
permissions:
  contents: read
```

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
