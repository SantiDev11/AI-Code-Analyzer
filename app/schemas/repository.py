"""Modelos de datos (contrato) que expone la API.

Estos modelos NO representan lo que devuelve GitHub, sino lo que devolvemos
nosotros. La traduccion entre ambos formatos ocurre en app/services/github.py.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class Repository(BaseModel):
    """Datos generales de un repositorio de GitHub."""

    name: str = Field(description="Nombre del repositorio")
    description: str | None = Field(
        description="Descripcion del repositorio, o null si no tiene"
    )
    stars: int = Field(description="Numero de estrellas")
    forks: int = Field(description="Numero de forks")
    open_issues: int = Field(description="Issues abiertas (incluye pull requests)")
    created_at: datetime = Field(description="Fecha de creacion (UTC)")
    updated_at: datetime = Field(description="Fecha de ultima actualizacion (UTC)")
    primary_language: str | None = Field(
        description="Lenguaje predominante, o null si GitHub no lo detecta"
    )
    url: str = Field(description="URL publica del repositorio")


class AnalysisResponse(BaseModel):
    """Respuesta completa del endpoint GET /analyze/{owner}/{repo}."""

    repository: Repository
    languages: dict[str, int] = Field(
        description="Lenguajes detectados y bytes de codigo de cada uno"
    )
    contributors_count: int | None = Field(
        description=(
            "Numero total de contribuidores, o null si GitHub se niega a "
            "calcularlo (ocurre en repositorios con un historial enorme)"
        )
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "repository": {
                    "name": "fastapi",
                    "description": "FastAPI framework, high performance",
                    "stars": 78000,
                    "forks": 6600,
                    "open_issues": 32,
                    "created_at": "2018-12-08T08:21:47Z",
                    "updated_at": "2024-05-02T08:12:44Z",
                    "primary_language": "Python",
                    "url": "https://github.com/fastapi/fastapi",
                },
                "languages": {"Python": 1245678, "HTML": 4321},
                "contributors_count": 654,
            }
        }
    }
