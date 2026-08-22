"""Calculo de metricas objetivas a partir de la estructura del Git Tree.

Este modulo no habla con GitHub ni con el disco: recibe los elementos del
arbol de archivos y calcula metricas cuantitativas de forma pura.
NO ejecuta nada del repositorio, NO descarga archivos y NO calcula lineas
de codigo inventadas (LOC permanece null).
"""

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import PurePosixPath

from app.schemas.repository import LargeFile, Metrics

# Maximo numero de archivos grandes incluidos en la respuesta
LARGEST_FILES_LIMIT = 10

# Extensiones reconocidas como codigo fuente
SOURCE_EXTENSIONS = frozenset(
    {
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".go",
        ".rs",
        ".java",
        ".c",
        ".cpp",
        ".cc",
        ".cxx",
        ".h",
        ".hpp",
        ".cs",
        ".rb",
        ".php",
        ".swift",
        ".kt",
        ".kts",
        ".scala",
        ".html",
        ".htm",
        ".css",
        ".scss",
        ".sass",
        ".less",
        ".vue",
        ".svelte",
        ".sql",
        ".sh",
        ".bash",
        ".zsh",
        ".r",
        ".m",
        ".dart",
        ".lua",
        ".zig",
        ".pl",
        ".pm",
        ".ex",
        ".exs",
        ".erl",
        ".clj",
        ".hs",
    }
)

# Carpetas tipicas de tests
TEST_DIRS = frozenset({"test", "tests", "spec", "specs", "__tests__"})

# Patrones de nombres de archivos de tests
TEST_FILE_PATTERNS = (
    "test_*.py",
    "*_test.py",
    "*_test.go",
    "*_test.rb",
    "*.test.js",
    "*.test.jsx",
    "*.test.ts",
    "*.test.tsx",
    "*.spec.js",
    "*.spec.jsx",
    "*.spec.ts",
    "*.spec.tsx",
)

# Documentacion especifica
DOC_PREFIXES = ("readme", "contributing", "changelog", "license", "authors", "notice", "code_of_conduct")
DOC_DIRS = frozenset({"docs", "doc", "documentation"})
DOC_EXTENSIONS = frozenset({".md", ".rst", ".adoc", ".asciidoc", ".pdf"})

# Archivos de configuracion conocidos
CONFIG_EXACT_NAMES = frozenset(
    {
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "tox.ini",
        "pipfile",
        "pipfile.lock",
        "poetry.lock",
        "package.json",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "tsconfig.json",
        "jsconfig.json",
        "dockerfile",
        "containerfile",
        "makefile",
        "gemfile",
        "gemfile.lock",
        "cargo.toml",
        "cargo.lock",
        "go.mod",
        "go.sum",
        "pom.xml",
        "build.gradle",
        "settings.gradle",
        "composer.json",
        "composer.lock",
        ".gitignore",
        ".gitattributes",
        ".editorconfig",
        ".flake8",
        "ruff.toml",
        ".ruff.toml",
        ".pylintrc",
        "pylintrc",
        ".pre-commit-config.yaml",
        ".rubocop.yml",
        ".golangci.yml",
        "clippy.toml",
        "mypy.ini",
        ".mypy.ini",
        "pyrightconfig.json",
        ".coveragerc",
        "codecov.yml",
        ".codecov.yml",
        ".env.example",
        "docker-compose.yml",
        "docker-compose.yaml",
        "jenkinsfile",
        ".travis.yml",
        ".gitlab-ci.yml",
        "azure-pipelines.yml",
        "appveyor.yml",
    }
)

CONFIG_PATTERNS = (
    ".eslintrc*",
    "eslint.config.*",
    ".prettierrc*",
    "prettier.config.*",
    ".stylelintrc*",
    "requirements*.txt",
    "docker-compose*.yml",
    "docker-compose*.yaml",
)


@dataclass(frozen=True)
class TreeEntry:
    """Entrada del arbol de git de GitHub."""

    path: str
    type: str = "blob"
    size: int | None = None


def _extract_extension(path: str) -> str:
    """Extrae la extension normalizada en minusculas.

    Archivos sin extension o con nombres tipo '.gitignore' devuelven '' o '.gitignore'.
    """
    pure = PurePosixPath(path)
    suffix = pure.suffix.lower()
    return suffix


def _is_test_file(path_lower: str) -> bool:
    """True si la ruta corresponde a un archivo de tests."""
    segments = path_lower.split("/")
    filename = segments[-1]
    dir_segments = segments[:-1]

    if any(segment in TEST_DIRS for segment in dir_segments):
        return True

    return any(fnmatch(filename, pattern) for pattern in TEST_FILE_PATTERNS)


def _is_doc_file(path_lower: str) -> bool:
    """True si la ruta corresponde a documentacion."""
    segments = path_lower.split("/")
    filename = segments[-1]
    dir_segments = segments[:-1]

    if any(segment in DOC_DIRS for segment in dir_segments):
        return True

    name_without_ext = filename.rsplit(".", 1)[0]
    if any(name_without_ext == prefix for prefix in DOC_PREFIXES):
        return True

    ext = PurePosixPath(path_lower).suffix.lower()
    return ext in DOC_EXTENSIONS


def _is_config_file(path_lower: str) -> bool:
    """True si la ruta corresponde a un archivo de configuracion conocido."""
    if path_lower.startswith(".github/") or path_lower.startswith(".circleci/"):
        return True

    filename = path_lower.rsplit("/", 1)[-1]
    if filename in CONFIG_EXACT_NAMES:
        return True

    return any(fnmatch(filename, pattern) for pattern in CONFIG_PATTERNS)


def _is_source_file(path_lower: str) -> bool:
    """True si es un archivo de codigo fuente que no es de test."""
    if _is_test_file(path_lower):
        return False

    ext = PurePosixPath(path_lower).suffix.lower()
    return ext in SOURCE_EXTENSIONS


def analyze_metrics(
    entries: Iterable[TreeEntry],
    *,
    available: bool = True,
    truncated: bool = False,
    largest_limit: int = LARGEST_FILES_LIMIT,
) -> Metrics:
    """Calcula metricas cuantitativas a partir de las entradas del Git Tree."""
    if not available:
        return Metrics(
            tree_available=False,
            tree_truncated=False,
            total_files=0,
            total_directories=0,
            source_files=0,
            test_files=0,
            documentation_files=0,
            configuration_files=0,
            file_extensions={},
            largest_files=[],
            lines_of_code=None,
        )

    file_entries: list[TreeEntry] = []
    all_directories: set[str] = set()

    for entry in entries:
        if entry.type == "tree":
            all_directories.add(entry.path.lower())
        else:
            file_entries.append(entry)
            # Deducir directorios padres
            parts = entry.path.lower().split("/")[:-1]
            for i in range(1, len(parts) + 1):
                all_directories.add("/".join(parts[:i]))

    # Extensiones de archivos
    extensions_counter: Counter[str] = Counter()
    source_count = 0
    test_count = 0
    doc_count = 0
    config_count = 0

    for entry in file_entries:
        path_lower = entry.path.lower()
        ext = _extract_extension(entry.path)
        extensions_counter[ext] += 1

        if _is_test_file(path_lower):
            test_count += 1
        elif _is_source_file(path_lower):
            source_count += 1

        if _is_doc_file(path_lower):
            doc_count += 1

        if _is_config_file(path_lower):
            config_count += 1

    # Archivos mas grandes
    files_with_size = [
        LargeFile(path=e.path, size_bytes=e.size)
        for e in file_entries
        if e.size is not None
    ]
    files_with_size.sort(key=lambda item: item.size_bytes, reverse=True)
    largest_files = files_with_size[:largest_limit]

    return Metrics(
        tree_available=True,
        tree_truncated=truncated,
        total_files=len(file_entries),
        total_directories=len(all_directories),
        source_files=source_count,
        test_files=test_count,
        documentation_files=doc_count,
        configuration_files=config_count,
        file_extensions=dict(sorted(extensions_counter.items(), key=lambda x: x[1], reverse=True)),
        largest_files=largest_files,
        lines_of_code=None,
    )
