"""Modelos de datos (contrato) que expone la API.

Estos modelos NO representan lo que devuelve GitHub, sino lo que devolvemos
nosotros. La traduccion entre ambos formatos ocurre en app/services/github.py.
"""

# `date` se importa con alias porque DailyActivity tiene un campo llamado
# `date`: el nombre del campo taparia al del tipo dentro de la clase.
from datetime import date as _Date
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
    default_branch: str = Field(
        default="main", description="Rama por defecto del repositorio"
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


class PullRequest(BaseModel):
    """Un pull request del repositorio.

    Viene de /pulls, no de /issues: aunque GitHub sirva los pull requests por
    los dos sitios, solo este endpoint trae la fecha de merge y las ramas.

    `state` y `merged_at` son dos ejes independientes, no tres estados: un
    pull request mergeado esta cerrado y ademas tiene fecha de merge.
    """

    number: int = Field(description="Numero del pull request dentro del repositorio")
    title: str = Field(description="Titulo del pull request")
    state: Literal["open", "closed"] = Field(description="Si esta abierto o cerrado")
    author: str | None = Field(
        description="Quien lo abrio, o null si la cuenta ya no existe"
    )
    created_at: datetime = Field(description="Fecha de apertura (UTC)")
    updated_at: datetime = Field(description="Fecha de la ultima actualizacion (UTC)")
    closed_at: datetime | None = Field(
        description="Fecha de cierre (UTC), o null si sigue abierto"
    )
    merged_at: datetime | None = Field(
        description="Fecha del merge (UTC), o null si no se llego a mergear"
    )
    source_branch: str | None = Field(
        description="Rama de origen, o null si GitHub ya no la informa"
    )
    target_branch: str | None = Field(
        description="Rama de destino, o null si GitHub ya no la informa"
    )
    url: str = Field(description="URL del pull request en GitHub")


class ReleaseDetail(BaseModel):
    """Un release del historial del repositorio.

    Es mas completo que `Release`, que solo describe la ultima version
    publicada: aqui hacen falta los dos indicadores de estado para poder
    contarlos por separado.

    `draft` y `prerelease` son dos ejes independientes, no tres estados: un
    release publicado puede estar marcado como prerelease, y un borrador
    puede llevar prerelease sin haberse publicado nunca.
    """

    id: int = Field(description="Identificador del release en GitHub")
    tag_name: str = Field(description="Etiqueta de la version, por ejemplo 'v1.2.0'")
    name: str | None = Field(description="Titulo del release, o null si no tiene")
    body: str | None = Field(description="Notas de la version, o null si no tiene")
    draft: bool = Field(description="True si es un borrador que no se ha publicado")
    prerelease: bool = Field(description="True si esta marcado como version previa")
    created_at: datetime = Field(description="Fecha de creacion (UTC)")
    published_at: datetime | None = Field(
        description="Fecha de publicacion (UTC), o null si sigue siendo un borrador"
    )
    author: str | None = Field(
        description="Quien lo publico, o null si la cuenta ya no existe"
    )
    url: str = Field(description="URL del release en GitHub")


class DailyActivity(BaseModel):
    """Actividad de un unico dia natural.

    Solo aparecen los dias que tuvieron algo; los dias vacios se omiten en
    lugar de rellenar la lista con ceros.
    """

    date: _Date = Field(description="Dia al que corresponden los recuentos (UTC)")
    commits: int = Field(description="Commits con fecha de ese dia")
    issues: int = Field(description="Issues abiertos ese dia")
    pull_requests_opened: int = Field(description="Pull requests abiertos ese dia")
    pull_requests_closed: int = Field(description="Pull requests cerrados ese dia")
    releases: int = Field(description="Releases publicados ese dia")


class Activity(BaseModel):
    """Actividad reciente del repositorio, repartida por dia.

    Se calcula a partir de los commits, issues, pull requests y releases que
    ya trae este mismo analisis: no cuesta ninguna peticion extra a GitHub.

    Eso tiene una consecuencia importante: esas listas son **muestras
    limitadas** (10 elementos de cada por defecto). Los totales cuentan lo que
    hay en la muestra dentro del periodo, asi que en un repositorio muy activo
    son un minimo, no la cifra real. Subir `commits`, `issues`, `pulls` y
    `releases` acerca ambas cifras.

    Todas las fechas se agrupan por dia **UTC**, que es la zona en la que
    GitHub publica sus timestamps.
    """

    days: int = Field(description="Dias naturales que abarca el periodo, contando hoy")
    since: _Date = Field(description="Primer dia del periodo (UTC), incluido")
    until: _Date = Field(description="Ultimo dia del periodo (UTC), incluido: hoy")
    total_commits: int = Field(description="Commits del periodo en la muestra analizada")
    total_issues: int = Field(description="Issues abiertos en el periodo")
    total_pull_requests: int = Field(
        description="Pull requests abiertos en el periodo. Los cerrados se ven en `daily`"
    )
    total_releases: int = Field(
        description="Releases publicados en el periodo. Los borradores no cuentan"
    )
    daily: list[DailyActivity] = Field(
        description="Dias con actividad, del mas reciente al mas antiguo"
    )


class QualitySignal(BaseModel):
    """Senal de deteccion de una herramienta o archivo de configuracion.

    detected es True si se encontraron archivos, False si el arbol completo
    demuestra su ausencia, o null si el arbol no estaba disponible o fue truncado.
    """

    detected: bool | None = Field(
        description="True si se detecto, False si no existe, null si el arbol no estaba disponible o fue truncado"
    )
    files: list[str] = Field(
        default_factory=list,
        description="Rutas relativas de los archivos detectados",
    )


class TestsSignal(BaseModel):
    """Senal de deteccion del suite de tests."""

    __test__ = False

    detected: bool | None = Field(
        description="True si se detectaron tests, False si no existen, null si no disponible/truncado"
    )
    files: int = Field(
        default=0,
        description="Numero de archivos de test detectados",
    )
    directories: list[str] = Field(
        default_factory=list,
        description="Directorios que contienen tests",
    )


class DocumentationSignal(BaseModel):
    """Senal de deteccion de documentacion del repositorio."""

    readme: bool | None = Field(
        description="True si se encontro README, False si no, null si no disponible/truncado"
    )
    contributing: bool | None = Field(
        description="True si se encontro CONTRIBUTING, False si no, null si no disponible/truncado"
    )
    docs_directory: bool | None = Field(
        description="True si existe directorio docs/, False si no, null si no disponible/truncado"
    )
    files: list[str] = Field(
        default_factory=list,
        description="Archivos principales de documentacion encontrados",
    )


class CoverageSignal(BaseModel):
    """Senal de deteccion de cobertura de codigo."""

    configured: bool | None = Field(
        description="True si hay archivos de configuracion de cobertura, False si no, null si no disponible/truncado"
    )
    percentage: float | None = Field(
        default=None,
        description="Porcentaje de cobertura si esta disponible (null ya que no ejecutamos codigo)",
    )
    files: list[str] = Field(
        default_factory=list,
        description="Archivos de configuracion de cobertura encontrados",
    )


class Quality(BaseModel):
    """Metricas e indicadores de calidad de codigo basados en la estructura de archivos."""

    tree_available: bool = Field(
        description="True si se pudo obtener el arbol de archivos de GitHub"
    )
    tree_truncated: bool = Field(
        description="True si GitHub trunco el arbol de archivos por tamano"
    )
    files_scanned: int = Field(
        description="Numero total de rutas analizadas en el arbol"
    )
    tests: TestsSignal = Field(description="Senales del suite de pruebas")
    documentation: DocumentationSignal = Field(
        description="Senales de documentacion"
    )
    ci: QualitySignal = Field(description="Integracion continua")
    linting: QualitySignal = Field(description="Linters y analisis estatico")
    formatting: QualitySignal = Field(description="Formateadores de codigo")
    type_checking: QualitySignal = Field(description="Comprobadores de tipos")
    dependencies: QualitySignal = Field(description="Gestion de dependencias")
    coverage: CoverageSignal = Field(description="Configuracion de cobertura")
    undetermined_config: list[str] = Field(
        default_factory=list,
        description="Archivos de configuracion genericos o indeterminados",
    )


class LargeFile(BaseModel):
    """Un archivo de gran tamano dentro del repositorio."""

    path: str = Field(description="Ruta relativa del archivo")
    size_bytes: int = Field(description="Tamano del archivo en bytes")


class Metrics(BaseModel):
    """Metricas objetivas de la base de codigo a partir del Git Tree."""

    tree_available: bool = Field(
        description="True si el arbol de archivos estuvo disponible para calcular metricas"
    )
    tree_truncated: bool = Field(
        description="True si GitHub trunco el arbol por superar el limite de elementos"
    )
    total_files: int = Field(description="Numero total de archivos en el repositorio")
    total_directories: int = Field(
        description="Numero total de directorios detectados en la estructura"
    )
    source_files: int = Field(
        description="Numero de archivos de codigo fuente (excluyendo tests)"
    )
    test_files: int = Field(description="Numero de archivos de tests")
    documentation_files: int = Field(
        description="Numero de archivos de documentacion (README, docs, markdown, etc.)"
    )
    configuration_files: int = Field(
        description="Numero de archivos de configuracion (linters, CI, build, etc.)"
    )
    file_extensions: dict[str, int] = Field(
        default_factory=dict,
        description="Recuento de archivos por extension (ej. {'.py': 42})",
    )
    largest_files: list[LargeFile] = Field(
        default_factory=list,
        description="Archivos mas pesados del repositorio por tamano en bytes",
    )
    lines_of_code: int | None = Field(
        default=None,
        description="Lineas de codigo (null: no se calculan sin descargar el contenido completo)",
    )


class Concern(BaseModel):
    """Aspecto de preocupacion o atencion fundamentado en datos del repositorio."""

    title: str = Field(description="Titulo resumido del aspecto de atencion")
    description: str = Field(description="Explicacion detallada del hallazgo")
    severity: Literal["low", "medium", "high"] = Field(
        description="Nivel de severidad justificado con datos"
    )
    evidence: str = Field(
        description="Evidencia concreta obtenida de las metricas, calidad o metadatos"
    )


class Recommendation(BaseModel):
    """Recomendacion tecnica accionable para el repositorio."""

    title: str = Field(description="Accion concreta sugerida")
    description: str = Field(description="Detalles de como implementar la mejora")
    priority: Literal["low", "medium", "high"] = Field(
        description="Prioridad de implementacion"
    )


class TechnicalOverview(BaseModel):
    """Vision tecnica general del repositorio."""

    architecture: str = Field(
        description="Resumen de la arquitectura deducida de la estructura"
    )
    stack: str = Field(description="Resumen del stack tecnologico principal")
    activity_summary: str = Field(
        description="Resumen del ritmo y estado de actividad reciente"
    )


class AIAnalysis(BaseModel):
    """Analisis tecnico estructurado generado mediante Inteligencia Artificial."""

    summary: str = Field(
        description="Resumen ejecutivo del estado del repositorio fundamentado en evidencia"
    )
    strengths: list[str] = Field(
        default_factory=list,
        description="Puntos fuertes del proyecto respaldados por datos",
    )
    concerns: list[Concern] = Field(
        default_factory=list,
        description="Puntos de atencion con evidencia demostrada",
    )
    recommendations: list[Recommendation] = Field(
        default_factory=list,
        description="Recomendaciones tecnicas accionables",
    )
    technical_overview: TechnicalOverview = Field(
        description="Vision tecnica general de arquitectura, stack y actividad"
    )


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
    pull_requests: list[PullRequest] = Field(
        description=(
            "Pull requests analizados, del mas reciente al mas antiguo. Es una "
            "muestra reciente, no el historial completo del repositorio"
        )
    )
    pull_requests_count: int = Field(
        description="Cuantos pull requests incluye la lista `pull_requests`"
    )
    open_pull_requests_count: int = Field(
        description="Cuantos de esos pull requests siguen abiertos"
    )
    closed_pull_requests_count: int = Field(
        description=(
            "Cuantos de esos pull requests estan cerrados. Los mergeados "
            "tambien estan cerrados, asi que cuentan aqui"
        )
    )
    merged_pull_requests_count: int = Field(
        description="Cuantos de esos pull requests se llegaron a mergear"
    )
    releases: list[ReleaseDetail] = Field(
        description=(
            "Historial de versiones en el orden que lo devuelve GitHub, del "
            "mas reciente al mas antiguo. Es una muestra, no el historial "
            "completo del repositorio"
        )
    )
    releases_count: int = Field(
        description="Cuantos releases incluye la lista `releases`"
    )
    published_releases_count: int = Field(
        description=(
            "Cuantos de esos releases estan publicados, es decir, no son "
            "borradores. Las versiones previas tambien estan publicadas, asi "
            "que cuentan aqui"
        )
    )
    draft_releases_count: int = Field(
        description="Cuantos de esos releases son borradores sin publicar"
    )
    prereleases_count: int = Field(
        description="Cuantos de esos releases estan marcados como version previa"
    )
    activity: Activity = Field(
        description="Actividad reciente por dia, calculada con los datos ya analizados"
    )
    quality: Quality = Field(
        description="Senales de calidad de codigo deducidas de la estructura de archivos"
    )
    metrics: Metrics = Field(
        description="Metricas cuantitativas de archivos y estructura de codigo"
    )
    ai_analysis: AIAnalysis | None = Field(
        default=None,
        description=(
            "Analisis tecnico estructurado por IA, o null si la IA no esta configurada o no disponible"
        ),
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
                    "default_branch": "main",
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
                "pull_requests": [
                    {
                        "number": 12,
                        "title": "Improve error handling",
                        "state": "closed",
                        "author": "SantiDev11",
                        "created_at": "2026-08-20T10:00:00Z",
                        "updated_at": "2026-08-21T10:00:00Z",
                        "closed_at": "2026-08-21T09:30:00Z",
                        "merged_at": "2026-08-21T09:30:00Z",
                        "source_branch": "fix/error-handling",
                        "target_branch": "main",
                        "url": "https://github.com/fastapi/fastapi/pull/12",
                    }
                ],
                "pull_requests_count": 1,
                "open_pull_requests_count": 0,
                "closed_pull_requests_count": 1,
                "merged_pull_requests_count": 1,
                "releases": [
                    {
                        "id": 178123456,
                        "tag_name": "0.115.0",
                        "name": "0.115.0",
                        "body": "Correcciones menores y mejoras de rendimiento.",
                        "draft": False,
                        "prerelease": False,
                        "created_at": "2024-04-20T09:30:00Z",
                        "published_at": "2024-04-20T10:00:00Z",
                        "author": "tiangolo",
                        "url": "https://github.com/fastapi/fastapi/releases/tag/0.115.0",
                    }
                ],
                "releases_count": 1,
                "published_releases_count": 1,
                "draft_releases_count": 0,
                "prereleases_count": 0,
                "activity": {
                    "days": 30,
                    "since": "2024-04-01",
                    "until": "2024-04-30",
                    "total_commits": 1,
                    "total_issues": 0,
                    "total_pull_requests": 0,
                    "total_releases": 1,
                    "daily": [
                        {
                            "date": "2024-04-20",
                            "commits": 1,
                            "issues": 0,
                            "pull_requests_opened": 0,
                            "pull_requests_closed": 0,
                            "releases": 1,
                        }
                    ],
                },
                "quality": {
                    "tree_available": True,
                    "tree_truncated": False,
                    "files_scanned": 150,
                    "tests": {
                        "detected": True,
                        "files": 12,
                        "directories": ["tests"],
                    },
                    "documentation": {
                        "readme": True,
                        "contributing": True,
                        "docs_directory": True,
                        "files": ["readme.md", "contributing.md"],
                    },
                    "ci": {
                        "detected": True,
                        "files": [".github/workflows/test.yml"],
                    },
                    "linting": {
                        "detected": True,
                        "files": [".flake8", "ruff.toml"],
                    },
                    "formatting": {
                        "detected": True,
                        "files": [".editorconfig"],
                    },
                    "type_checking": {
                        "detected": True,
                        "files": ["mypy.ini"],
                    },
                    "dependencies": {
                        "detected": True,
                        "files": ["pyproject.toml"],
                    },
                    "coverage": {
                        "configured": True,
                        "percentage": None,
                        "files": [".coveragerc"],
                    },
                    "undetermined_config": ["pyproject.toml"],
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
                        ".yml": 2,
                    },
                    "largest_files": [
                        {
                            "path": "fastapi/applications.py",
                            "size_bytes": 18450,
                        }
                    ],
                    "lines_of_code": None,
                },
                "ai_analysis": {
                    "summary": "FastAPI es un framework web maduro, altamente probado y con activa mantencion.",
                    "strengths": [
                        "Suite de pruebas robusta con amplia cobertura de casos de uso.",
                        "Documentacion extensa y actualizada en multiples idiomas.",
                    ],
                    "concerns": [
                        {
                            "title": "Configuracion de cobertura no detectada en raiz",
                            "description": "No se identifico archivo .coveragerc explicito.",
                            "severity": "low",
                            "evidence": "CoverageSignal detected=False en archivos analizados.",
                        }
                    ],
                    "recommendations": [
                        {
                            "title": "Asegurar reporte publico de cobertura",
                            "description": "Integrar reporte de Codecov en el flujo de CI.",
                            "priority": "low",
                        }
                    ],
                    "technical_overview": {
                        "architecture": "Framework basado en Starlette y Pydantic estructurado modularmente.",
                        "stack": "Python, Starlette, Pydantic, Uvicorn, pytest.",
                        "activity_summary": "Actividad constante con releases periodicos y gestion activa de PRs.",
                    },
                },
                "cached": False,
            }
        }
    }
