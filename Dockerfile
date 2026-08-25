# ---------------------------------------------------------------------------
# AI-Code-Analyzer — Backend (FastAPI + Uvicorn)
#
# La imagen contiene solamente el codigo de la aplicacion y sus dependencias.
# Ningun secreto (GITHUB_TOKEN, AI_API_KEY) se copia ni se declara aqui: se
# inyectan como variables de entorno al arrancar el contenedor.
# ---------------------------------------------------------------------------
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /srv

# Las dependencias se instalan antes de copiar el codigo para que la capa
# quede cacheada mientras requirements.txt no cambie.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Usuario sin privilegios: la aplicacion no necesita root para escuchar en 8000.
RUN useradd --create-home --uid 1000 appuser

COPY --chown=appuser:appuser app ./app

USER appuser

# Puerto de la API dentro del contenedor.
EXPOSE 8000

# Healthcheck contra el endpoint ya existente /health, sin instalar curl.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).status == 200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
