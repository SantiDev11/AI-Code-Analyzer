# ---------------------------------------------------------------------------
# AI-Code-Analyzer — Servicio Unificado (FastAPI + React Frontend)
#
# Multi-stage build:
#   Stage 1 (frontend-builder): Node 22 compila la aplicacion React/Vite.
#   Stage 2 (runtime): Python 3.12 ejecuta FastAPI sirviendo la API y el bundle estatico.
#
# Ningun secreto (GITHUB_TOKEN, AI_API_KEY) se copia ni se declara aqui: se
# inyectan como variables de entorno al arrancar el contenedor.
# ---------------------------------------------------------------------------

# Stage 1: Compilacion del Frontend React
FROM node:22-alpine AS frontend-builder

WORKDIR /build

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Runtime FastAPI + Frontend estatico
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /srv

# Instalacion de dependencias Python con cacheo de capa
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Usuario sin privilegios por seguridad
RUN useradd --create-home --uid 1000 appuser

# Copia del backend y de los artefactos compilados del frontend
COPY --chown=appuser:appuser app ./app
COPY --from=frontend-builder --chown=appuser:appuser /build/dist ./frontend/dist

USER appuser

# Puerto unico de la aplicacion
EXPOSE 8000

# Healthcheck nativo contra /health
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).status == 200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

