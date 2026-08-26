"""Punto de entrada de la aplicacion unificada (FastAPI + React Frontend).

Arrancar en desarrollo con:
    uvicorn app.main:app --reload
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.config import settings

# Ubicacion del build del frontend React (Vite).
# En produccion/Docker o tras `npm run build`, se ubica en frontend/dist.
# Si no existe todavia, recurre a app/static como fallback.
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
STATIC_FALLBACK = Path(__file__).resolve().parent / "static"
STATIC_DIR = FRONTEND_DIST if (FRONTEND_DIST / "index.html").is_file() else STATIC_FALLBACK

app = FastAPI(
    title="AI-Code-Analyzer",
    description="Analiza repositorios publicos de GitHub usando la GitHub REST API e Inteligencia Artificial.",
    version="0.1.0",
)

# Origenes permitidos, configurables con CORS_ALLOWED_ORIGINS.
# En la arquitectura unificada el frontend y backend comparten el mismo origen,
# pero se mantiene CORS para desarrollo local desacoplado (ej. Vite en puerto 3000/5173).
ALLOWED_ORIGINS = settings.cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

# 1. Endpoints de la API
app.include_router(router)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    """Comprueba que el servicio esta vivo."""
    return {"status": "ok"}


# 2. Servir carpetas de assets estaticos
if (STATIC_DIR / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

if (STATIC_DIR / "static").is_dir():
    app.mount("/static", StaticFiles(directory=STATIC_DIR / "static"), name="static")
elif STATIC_FALLBACK.is_dir():
    app.mount("/static", StaticFiles(directory=STATIC_FALLBACK), name="static")


# 3. Servir frontend SPA y fallback para client-side routing
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa_or_static(full_path: str = "") -> FileResponse:
    """Sirve la aplicacion SPA de React o archivos estaticos en la raiz del build.

    Las rutas prioritarias (/health, /docs, /openapi.json, /analyze/..., /assets/...)
    son capturadas antes por FastAPI. Si se solicita un archivo estatico especifico
    existente (ej. favicon.ico, vite.svg, robots.txt), se devuelve directamente.
    Cualquier otra ruta web devuelve index.html para soportar client-side routing.
    """
    if full_path:
        requested_file = STATIC_DIR / full_path
        if requested_file.is_file():
            return FileResponse(requested_file)

    index_file = STATIC_DIR / "index.html"
    if index_file.is_file():
        return FileResponse(index_file)

    raise HTTPException(status_code=404, detail="Frontend build not found")

