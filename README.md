# AI-Code-Analyzer

[![CI](https://github.com/SantiDev11/AI-Code-Analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/SantiDev11/AI-Code-Analyzer/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-6-646CFF?logo=vite&logoColor=white)](https://vite.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)

**Aplicación web que radiografía cualquier repositorio público de GitHub.**

Escribes un propietario y un repositorio, y obtienes en un solo panel lo que normalmente exige abrir diez pestañas: metadatos, lenguajes, colaboradores, commits, issues, pull requests, releases, actividad, señales de calidad, métricas de estructura y un análisis técnico generado por Inteligencia Artificial.

- 🔗 **Datos reales de la GitHub REST API**, consultados en el momento.
- 🤖 **AI Analysis** fundamentado estrictamente en la evidencia recogida.
- 🔒 **Nunca ejecuta el código analizado**: solo lee metadatos y el árbol de archivos.
- 📦 **Arquitectura unificada**: React y FastAPI viajan en la misma imagen y comparten origen.

El flujo principal es el **frontend**: el usuario abre una URL, rellena el formulario y explora los resultados sin salir de la interfaz. Detrás, FastAPI actúa como motor de análisis y sirve además la propia aplicación React. La API queda accesible por si quieres consumirla directamente (ver [Endpoints](#endpoints)), pero no es el camino previsto para el usuario final.

---

## 🚀 Demo

### ▶️ [**Probar AI-Code-Analyzer**](https://ai-code-analyzer-1-qm5f.onrender.com)

**No necesitas instalar nada para probar la versión desplegada.**

> ℹ️ La demo corre en el plan gratuito de Render: si lleva un rato inactiva, la primera petición puede tardar unos segundos en despertarla. Además **no tiene `AI_API_KEY` configurada**, así que `ai_analysis` llega como `null`; el resto del análisis funciona con normalidad.

---

## ⚡ Cómo usarlo

1. Abre la [demo](https://ai-code-analyzer-1-qm5f.onrender.com) — o <http://localhost:8000> si lo ejecutas en local.
2. Escribe el **propietario u organización** de GitHub — por ejemplo `encode`.
3. Escribe el **repositorio** — por ejemplo `httpx`.
4. Pulsa **Analyze Repository**.
5. Explora el panel: cada dimensión del análisis se despliega en su propia tarjeta.

Acepta cualquier **repositorio público** de GitHub. Los privados no son accesibles y devuelven un error explicativo.

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

### Variable pública del frontend

El frontend admite una única variable, declarada en `frontend/.env.example`:

| Variable | Por defecto | Descripción |
| --- | --- | --- |
| `VITE_API_BASE_URL` | vacía | URL base de la API. **Vacía** = peticiones relativas al mismo origen, que es lo que necesita la arquitectura unificada |

En la arquitectura unificada **debe quedarse vacía**: la interfaz y la API comparten origen, así que el cliente llama a `/analyze/...` de forma relativa. También sirve vacía durante el desarrollo con Vite, porque su proxy redirige `/analyze` y `/health` al backend.

> ⚠️ **Las variables `VITE_*` no son secretas.** Vite las sustituye por su valor literal **durante el build** y quedan incrustadas en el JavaScript que descarga cualquier visitante: se leen abriendo las DevTools. Nunca pongas ahí un token ni una clave de API — para eso están `GITHUB_TOKEN` y `AI_API_KEY`, que viven exclusivamente en el backend.
>
> Si alguna vez le das valor, debe ser una **URL pública alcanzable desde el navegador**, y cambiarla exige **reconstruir** el bundle: no basta con reiniciar el proceso.

---

## Instalación y Ejecución

### 1. Desarrollo Local Unificado o Backend (FastAPI)

Requiere **Python 3.12+**.

```bash
# 1. Crear y activar entorno virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. (Opcional) Compilar frontend para servirlo directamente desde FastAPI
cd frontend && npm install && npm run build && cd ..

# 4. Iniciar servidor
uvicorn app.main:app --reload
```

Accede a:
- <http://127.0.0.1:8000/> para la interfaz web React (si `frontend/dist` está compilado).
- <http://127.0.0.1:8000/docs> para explorar la API en Swagger UI.
- <http://127.0.0.1:8000/health> para comprobar el estado del servicio.

### 2. Desarrollo Frontend Independiente con Vite (HMR)

Requiere **Node.js 18+** y **npm**.

```bash
# 1. Navegar al directorio frontend e instalar dependencias
cd frontend
npm install

# 2. Iniciar servidor de desarrollo frontend con Hot Module Replacement
npm run dev

# 3. Comprobación estricta de tipos y compilación
npm run typecheck
npm run build
```

El servidor de desarrollo de Vite corre en <http://localhost:3000> y redirige automáticamente por proxy las peticiones `/analyze` y `/health` al backend en <http://localhost:8000>.

---

## Ejecución con Docker (Servicio Único Unificado)

Empaqueta la aplicación completa (**React + FastAPI**) en una sola imagen de producción optimizada mediante una compilación multi-stage.

### Prerequisitos

- **Docker Engine 24+** con plugin **Docker Compose v2** (`docker compose`).
- Docker Desktop activo en Windows o macOS.

### Arquitectura Unificada

Un único contenedor desplegable:

| Servicio | Imagen base / Etapas | Puerto interno | Puerto publicado |
| -------- | -------------------- | -------------- | ---------------- |
| `app`    | Multi-stage: `node:22-alpine` (build) + `python:3.12-slim` (runtime) | 8000 | `8000` |

El build de React se genera en el Stage 1 (`node:22-alpine`) y se transfiere al Stage 2 (`python:3.12-slim`). FastAPI sirve directamente la aplicación SPA en `/` y sus assets `/assets/...`, al tiempo que expone los endpoints `/analyze/{owner}/{repo}`, `/health` y `/docs`.

```
Navegador ──► http://localhost:8000 (FastAPI)
                   ├── /               ──► React Frontend (index.html)
                   ├── /assets/...     ──► JS / CSS estáticos compilados
                   ├── /analyze/...    ──► Análisis con GitHub API + IA
                   ├── /health         ──► Healthcheck
                   └── /docs           ──► Swagger UI
```

### Comandos Docker

```bash
# Construir la imagen unificada
docker compose build

# Levantar el servicio
docker compose up

# Construir y levantar en un solo paso
docker compose up --build

# Levantar en segundo plano
docker compose up -d

# Ver el estado y healthcheck
docker compose ps

# Detener y limpiar contenedores
docker compose down
```

### URLs

| Recurso            | URL                             |
| ------------------ | ------------------------------- |
| Aplicación Web     | <http://localhost:8000>         |
| Swagger UI         | <http://localhost:8000/docs>    |
| ReDoc              | <http://localhost:8000/redoc>   |
| Health check       | <http://localhost:8000/health>  |

### Variables de Entorno

Compose lee el archivo `.env` de la raíz (ignorado por git) e inyecta las variables en el contenedor. `.dockerignore` excluye `.env` del contexto de build, garantizando que ninguna credencial quede expuesta en las capas de la imagen.

**Variables secretas (exclusivamente en el backend):**

| Variable       | Descripción                                                      |
| -------------- | ---------------------------------------------------------------- |
| `GITHUB_TOKEN` | Token personal de GitHub. Eleva el rate limit de 60 a 5000 req/h. |
| `AI_API_KEY`   | Clave del proveedor de IA. Sin ella, `ai_analysis` devuelve `null`. |

> 🔒 **Seguridad:** `GITHUB_TOKEN` y `AI_API_KEY` residen únicamente en el backend. El frontend jamás recibe ni manipula estas claves.

**Variables de configuración:**

`AI_PROVIDER`, `AI_MODEL`, `AI_BASE_URL`, `AI_TIMEOUT_SECONDS`, `CACHE_TTL_SECONDS`, `ACTIVITY_DAYS`, `CORS_ALLOWED_ORIGINS`.

**Variable pública del frontend:** `VITE_API_BASE_URL` se resuelve **en tiempo de build**, dentro de la etapa de Node del `Dockerfile`. En la imagen unificada se deja vacía para que el bundle use rutas relativas. Nunca debe contener secretos ([detalle](#variable-pública-del-frontend)).

### CORS

Al servirse el frontend y la API bajo el mismo origen (`http://localhost:8000` o la URL única de producción en Render), **CORS no interviene en producción**. Se mantiene la configuración de `CORS_ALLOWED_ORIGINS` para permitir desarrollo local desacoplado (puertos 3000 o 5173).

### Despliegue en Render

Para desplegar la imagen unificada como un **único Web Service**:

1. Crear un **Web Service** conectado al repositorio.
2. Seleccionar entorno **Docker**.
3. Render construye la imagen con el `Dockerfile` multi-stage y expone la aplicación completa — interfaz y API — en **una sola URL pública**.
4. Definir las variables de entorno (`GITHUB_TOKEN`, `AI_API_KEY`, …) en el panel de Render.

Con un único servicio no hace falta tocar `CORS_ALLOWED_ORIGINS` ni `VITE_API_BASE_URL`: al compartir origen, no hay peticiones cross-origin.

**Despliegue actualmente en línea:**

| Servicio | URL |
| --- | --- |
| Aplicación web | <https://ai-code-analyzer-1-qm5f.onrender.com> |
| API | <https://ai-code-analyzer-viqi.onrender.com> |

> ℹ️ Esas dos URLs corresponden al despliegue **anterior**, hecho como dos servicios separados (interfaz y API en dominios distintos, comunicados por CORS). Siguen operativas y son las que abre la [demo](#-demo). La migración del despliegue al Web Service único descrito arriba **está pendiente**: el repositorio ya es unificado, la infraestructura todavía no.

---

## Ejecución de Tests

### Tests del Backend (pytest)

```bash
pip install -r requirements-dev.txt
pytest
```

Todas las pruebas del backend utilizan transportes simulados (`httpx.MockTransport`): no consumen cuota de la GitHub API ni realizan peticiones reales al proveedor de IA.

Cubren también la capa unificada: que `/docs` y `/openapi.json` sigan disponibles, que las rutas desconocidas devuelvan la SPA y que los archivos servidos no contengan secretos.

### Tests del Frontend (Vitest)

```bash
cd frontend
npm test
```

Las suites de pruebas del frontend renderizan los componentes de forma estática con datos mockeados y verifican accesibilidad semántica, ausencia de valores nulos o inválidos y gestión de estados.

| Suite | Estado actual |
| --- | --- |
| Backend (pytest) | **255 tests** |
| Frontend (Vitest) | **180 tests** en 13 archivos |

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

Las versiones no son arbitrarias: ambas salen del `Dockerfile` unificado — **Node 22** es la etapa que compila el frontend y **Python 3.12** la que ejecuta la aplicación en producción. La CI valida lo que realmente se despliega.

El caché de dependencias se apoya en los lockfiles (`requirements*.txt` y `frontend/package-lock.json`): al cambiar cualquiera de ellos, la clave de caché cambia y se reinstala desde cero.

### Qué hace fallar el pipeline

| Job        | Condición de fallo                                                                   |
| ---------- | ------------------------------------------------------------------------------------ |
| `backend`  | Cualquier test de `pytest` que falle, o un error instalando dependencias.             |
| `frontend` | Un test de Vitest en rojo, un error de tipos en `tsc`, o un fallo de `vite build`.    |
| `docker`   | `compose.yaml` inválido, o que la imagen unificada no construya.                      |

`npm run build` ejecuta `tsc && vite build`, así que un error de tipos también rompe el build además del paso de `typecheck`.

### Secretos

**La CI no necesita ningún secreto.** No se declaran `GITHUB_TOKEN` ni `AI_API_KEY` en el workflow: los tests del backend sustituyen el cliente HTTP por transportes simulados (`tests/conftest.py`), de modo que **no se llama a la GitHub API ni a ningún proveedor de IA** durante la ejecución.

El job de `docker` solo construye la imagen; **no publica nada** en ningún registro y **no despliega**: la publicación en Render se hace aparte.

Los permisos del token automático están reducidos al mínimo:

```yaml
permissions:
  contents: read
```

---

## Arquitectura Interna

```
Usuario (navegador)
                     ↓
Frontend React + TypeScript   ← punto principal del flujo: formulario y panel
                     ↓   GET /analyze/{owner}/{repo}   (mismo origen, sin CORS)
             app/main.py      ← sirve la SPA en "/", sus assets en "/assets" y monta la API
                     ↓
             app/api/routes.py ← valida parametros y traduce errores a codigos HTTP
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

Una sola aplicación cubre las dos capas: **el frontend concentra la interacción** — es lo único que ve el usuario — y el backend concentra el análisis. No hay lógica de análisis duplicada en el cliente: el navegador **no llama nunca a la GitHub API** directamente, lo que mantiene `GITHUB_TOKEN` y `AI_API_KEY` fuera del bundle.

---

## Limitaciones Conocidas

1. **Líneas de Código (`lines_of_code = null`):** La API de Git Tree proporciona tamaños en bytes (`size`), pero no contenidos. Para no saturar la cuota ni descargar repositorios completos, `lines_of_code` se mantiene como `null` explícito.
2. **Git Tree Truncado (`tree_truncated = True`):** En repositorios masivos (> 100,000 archivos), GitHub trunca el árbol. El sistema marca `tree_truncated: true` y evalúa únicamente sobre el subconjunto recibido sin asumir falsos negativos.
3. **Señales de Calidad Nulas:** Si el árbol de archivos no está disponible o fue truncado, las señales de calidad se marcan como `null` en lugar de `false`.
4. **Disponibilidad de IA:** `ai_analysis` depende de la conectividad y cuota del proveedor externo configurado. Ante errores del proveedor, rate limits o respuestas malformadas, el sistema degrada elegantemente devolviendo `ai_analysis: null` sin afectar la respuesta general.
5. **Aislamiento y Seguridad:** El backend **nunca** ejecuta archivos, scripts, `Makefile`, `package.json` ni dependencias del repositorio analizado.
6. **Rutas desconocidas devuelven la interfaz, no un 404:** para que el enrutado del lado del cliente funcione, cualquier ruta no reconocida responde `index.html` con código `200`. Efecto práctico: una ruta de API mal escrita (`/analize/...`, `/healht`) devuelve HTML con `200` en lugar de un `404` JSON. Los errores reales del análisis **sí** conservan su código: un repositorio inexistente sigue devolviendo `404` con su `detail`.
7. **Origen de los archivos servidos:** la aplicación sirve `frontend/dist` si encuentra ahí un `index.html`; si no existe, recurre a `app/static`, una maqueta estática sin JavaScript. Por eso, en un entorno donde el frontend no se haya compilado, la raíz muestra esa maqueta en vez de la aplicación React. Compilar con `npm run build` (o usar la imagen Docker, que lo hace sola) resuelve el caso.
