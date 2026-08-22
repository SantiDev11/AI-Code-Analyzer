"""Punto de entrada de la aplicacion.

Arrancar en desarrollo con:
    uvicorn app.main:app --reload
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router

# Archivos del frontend (HTML y CSS), servidos por la propia aplicacion.
STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="AI-Code-Analyzer",
    description="Analiza repositorios publicos de GitHub usando la GitHub REST API.",
    version="0.1.0",
)

app.include_router(router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    """Sirve la interfaz web."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    """Comprueba que el servicio esta vivo."""
    return {"status": "ok"}
