"""Modelos de datos (contrato) que expone la API.

Estos modelos NO representan lo que devuelve GitHub, sino lo que devolvemos
nosotros. La traduccion entre ambos formatos ocurre en app/services/github.py.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Repository(BaseModel):
    """Datos generales de un repositorio de GitHub."""

    name: str = Field(description="Nombre del repositorio")
    full_name: str = Field(
        description="Nombre completo con el propietario, por ejemplo 'encode/httpx'"
    )
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


class Contributor(BaseModel):
    """Una persona que ha contribuido al repositorio.

    Solo exponemos estos cuatro datos: GitHub devuelve una veintena de campos
    por contribuidor (node_id, gravatar_id, urls internas de la API...) que no
    aportan nada a quien consume nuestra respuesta.
    """

    username: str = Field(description="Nombre de usuario en GitHub")
    contributions: int = Field(description="Numero de commits atribuidos")
    avatar_url: str = Field(description="URL de la imagen de perfil")
    profile_url: str = Field(description="URL del perfil publico en GitHub")


class Release(BaseModel):
    """Ultima version publicada del repositorio."""

    tag: str = Field(description="Etiqueta de la version, por ejemplo 'v1.2.0'")
    name: str | None = Field(description="Titulo de la release, o null si no tiene")
    published_at: datetime = Field(description="Fecha de publicacion (UTC)")
    url: str = Field(description="URL de la release en GitHub")


class Issue(BaseModel):
    """Un issue del repositorio.

    Los pull requests se descartan antes de llegar aqui: GitHub los sirve por
    el mismo endpoint, pero no son issues.
    """

    number: int = Field(description="Numero del issue dentro del repositorio")
    title: str = Field(description="Titulo del issue")
    state: Literal["open", "closed"] = Field(description="Si esta abierto o cerrado")
    author: str | None = Field(
        description="Quien lo abrio, o null si la cuenta ya no existe"
    )
    created_at: datetime = Field(description="Fecha de apertura (UTC)")
    updated_at: datetime = Field(description="Fecha de la ultima actualizacion (UTC)")
    url: str = Field(description="URL del issue en GitHub")


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
    contributors: list[Contributor] = Field(
        description=(
            "Principales contribuidores, del que mas ha aportado al que menos. "
            "Es una seleccion de los mas activos, no la lista completa"
        )
    )
    contributors_count: int = Field(
        description="Cuantos contribuidores incluye la lista `contributors`"
    )
    latest_release: Release | None = Field(
        description="Ultima version publicada, o null si el repositorio no tiene"
    )
    recent_commits: list[Commit] = Field(
        description="Ultimos commits de la rama principal, del mas reciente al mas antiguo"
    )
    issues: list[Issue] = Field(
        description=(
            "Issues analizados, sin pull requests. Es una muestra reciente, "
            "no el historial completo del repositorio"
        )
    )
    issues_count: int = Field(description="Cuantos issues incluye la lista `issues`")
    open_issues_count: int = Field(description="Cuantos de esos issues estan abiertos")
    closed_issues_count: int = Field(description="Cuantos de esos issues estan cerrados")
    cached: bool = Field(
        default=False,
        description="True si la respuesta viene de la cache y no de GitHub",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "repository": {
                    "name": "fastapi",
                    "full_name": "fastapi/fastapi",
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
                "contributors": [
                    {
                        "username": "tiangolo",
                        "contributions": 1042,
                        "avatar_url": "https://avatars.githubusercontent.com/u/1326112",
                        "profile_url": "https://github.com/tiangolo",
                    }
                ],
                "contributors_count": 1,
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
                "issues": [
                    {
                        "number": 15,
                        "title": "Improve error handling",
                        "state": "open",
                        "author": "SantiDev11",
                        "created_at": "2026-08-22T10:30:00Z",
                        "updated_at": "2026-08-22T12:00:00Z",
                        "url": "https://github.com/fastapi/fastapi/issues/15",
                    }
                ],
                "issues_count": 1,
                "open_issues_count": 1,
                "closed_issues_count": 0,
                "cached": False,
            }
        }
    }
