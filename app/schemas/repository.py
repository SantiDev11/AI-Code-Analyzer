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
    license: str | None = Field(
        description="Identificador SPDX de la licencia, o null si no tiene"
    )
    topics: list[str] = Field(description="Etiquetas tematicas del repositorio")
    size_kb: int = Field(description="Tamano del repositorio en kilobytes")
    is_archived: bool = Field(
        description="True si el repositorio esta archivado (solo lectura)"
    )


class Release(BaseModel):
    """Ultima version publicada del repositorio."""

    tag: str = Field(description="Etiqueta de la version, por ejemplo 'v1.2.0'")
    name: str | None = Field(description="Titulo de la release, o null si no tiene")
    published_at: datetime = Field(description="Fecha de publicacion (UTC)")
    url: str = Field(description="URL de la release en GitHub")


class Commit(BaseModel):
    """Un commit del historial reciente."""

    sha: str = Field(description="Identificador corto del commit (7 caracteres)")
    message: str = Field(description="Primera linea del mensaje del commit")
    author: str | None = Field(description="Autor del commit, o null si se desconoce")
    date: datetime = Field(description="Fecha del commit (UTC)")
    url: str = Field(description="URL del commit en GitHub")


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
    latest_release: Release | None = Field(
        description="Ultima version publicada, o null si el repositorio no tiene"
    )
    recent_commits: list[Commit] = Field(
        description="Ultimos commits de la rama principal, del mas reciente al mas antiguo"
    )
    cached: bool = Field(
        default=False,
        description="True si la respuesta viene de la cache y no de GitHub",
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
                    "license": "MIT",
                    "topics": ["python", "api", "async"],
                    "size_kb": 40123,
                    "is_archived": False,
                },
                "languages": {"Python": 1245678, "HTML": 4321},
                "contributors_count": 654,
                "latest_release": {
                    "tag": "0.115.0",
                    "name": "0.115.0",
                    "published_at": "2024-04-20T10:00:00Z",
                    "url": "https://github.com/fastapi/fastapi/releases/tag/0.115.0",
                },
                "recent_commits": [
                    {
                        "sha": "a1b2c3d",
                        "message": "Fix typo in docs",
                        "author": "tiangolo",
                        "date": "2024-05-02T08:00:00Z",
                        "url": "https://github.com/fastapi/fastapi/commit/a1b2c3d",
                    }
                ],
                "cached": False,
            }
        }
    }
