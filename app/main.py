"""Punto de entrada de la aplicacion.

Arrancar en desarrollo con:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="AI-Code-Analyzer",
    description="Analiza repositorios publicos de GitHub usando la GitHub REST API.",
    version="0.1.0",
)

app.include_router(router)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    """Comprueba que el servicio esta vivo."""
    return {"status": "ok"}
