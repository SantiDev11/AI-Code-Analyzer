"""Deteccion de senales de calidad a partir de la lista de archivos.

Este modulo no habla con GitHub ni con el disco: recibe rutas y devuelve
senales. Y sobre todo **no ejecuta nada** del repositorio analizado. No
importa subprocess, no descarga el contenido de ningun archivo y no interpreta
configuraciones: solo compara nombres contra tablas conocidas.

De ahi la regla que gobierna todo el modulo: solo cuenta como evidencia lo que
el nombre de un archivo demuestra por si solo. Un pyproject.toml puede
configurar ruff, black y mypy... o ninguno de los tres. Sin leerlo no hay
forma de saberlo, asi que no se cuenta como linter ni como formateador: se
declara aparte, en `undetermined_config`.

La otra regla: no confundir "no lo encontre" con "no existe". Si GitHub trunca
el arbol, o no hay arbol, las ausencias se publican como null y no como false.
"""

from collections.abc import Iterable
from fnmatch import fnmatch

from app.schemas.repository import (
    CoverageSignal,
    DocumentationSignal,
    Quality,
    QualitySignal,
    TestsSignal,
)

# --------------------------------------------------------------------------
# Tablas de deteccion. Todo se compara en minusculas.
# --------------------------------------------------------------------------

# Carpetas que, por convencion, contienen tests en casi cualquier lenguaje.
# Cubre tambien src/test/java/... de Maven sin necesitar reglas de Java.
TEST_DIRS = frozenset({"test", "tests", "spec", "specs", "__tests__"})

# Nombres de archivo de test. No se incluyen los de Java o C# (FooTest.java)
# porque el patron equivalente picaria falsos positivos como "latest.java".
TEST_FILES = (
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

README = ("readme", "readme.md", "readme.rst", "readme.txt")
CONTRIBUTING = ("contributing", "contributing.md", "contributing.rst")

CI_FILES = (
    ".gitlab-ci.yml",
    ".travis.yml",
    "azure-pipelines.yml",
    "appveyor.yml",
    "jenkinsfile",
)

# Configuraciones que solo pueden pertenecer a un linter: si el archivo esta,
# hay linter configurado, sin ambiguedad posible.
LINTER_FILES = (
    ".flake8",
    "ruff.toml",
    ".ruff.toml",
    ".pylintrc",
    "pylintrc",
    "biome.json",
    ".pre-commit-config.yaml",
    ".rubocop.yml",
    ".golangci.yml",
    "clippy.toml",
)
LINTER_PATTERNS = (".eslintrc*", "eslint.config.*", ".stylelintrc*")

FORMATTER_FILES = (
    ".editorconfig",
    ".clang-format",
    "rustfmt.toml",
    ".rustfmt.toml",
    ".style.yapf",
)
FORMATTER_PATTERNS = (".prettierrc*", "prettier.config.*")

# tsconfig.json cuenta: usar TypeScript es comprobar tipos.
TYPE_FILES = (
    "mypy.ini",
    ".mypy.ini",
    "pyrightconfig.json",
    ".pyre_configuration",
    "tsconfig.json",
    "jsconfig.json",
)

DEPENDENCY_FILES = (
    "pyproject.toml",
    "setup.py",
    "pipfile",
    "poetry.lock",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "go.mod",
    "cargo.toml",
    "gemfile",
    "composer.json",
    "pom.xml",
    "build.gradle",
)
DEPENDENCY_PATTERNS = ("requirements*.txt",)

COVERAGE_FILES = (".coveragerc", "codecov.yml", ".codecov.yml", "codecov.yaml")

# Archivos que PUEDEN configurar linters, formateadores o type checkers, pero
# que tambien existen sin nada de eso dentro. Sin leerlos no se puede decidir,
# asi que no cuentan como evidencia de ninguna senal: se declaran aparte.
UNDETERMINED_FILES = (
    "pyproject.toml",
    "setup.cfg",
    "tox.ini",
    "package.json",
    "makefile",
)


# --------------------------------------------------------------------------
# Utilidades internas
# --------------------------------------------------------------------------


def _basename(path: str) -> str:
    return path.rsplit("/", 1)[-1]


def _matches(name: str, exactos: tuple[str, ...], patrones: tuple[str, ...] = ()) -> bool:
    return name in exactos or any(fnmatch(name, patron) for patron in patrones)


def _is_workflow(path: str) -> bool:
    """True para .github/workflows/algo.yml, que es CI sin ambiguedad."""
    return path.startswith(".github/workflows/") and path.endswith((".yml", ".yaml"))


def _is_circleci(path: str) -> bool:
    return path.startswith(".circleci/") and path.endswith((".yml", ".yaml"))


def _test_directory(path: str) -> str | None:
    """Devuelve el directorio de tests que contiene la ruta, si lo hay.

    Se mira cada segmento salvo el nombre del archivo, asi que tanto tests/
    como src/test/java/... quedan detectados.
    """
    segmentos = path.split("/")[:-1]
    for indice, segmento in enumerate(segmentos):
        if segmento in TEST_DIRS:
            return "/".join(segmentos[: indice + 1])
    return None


def _is_test(path: str) -> bool:
    return _test_directory(path) is not None or _matches(_basename(path), (), TEST_FILES)


# --------------------------------------------------------------------------
# Construccion de las senales
# --------------------------------------------------------------------------


def _signal(encontrados: list[str], *, available: bool, truncated: bool) -> QualitySignal:
    """Convierte una lista de hallazgos en una senal.

    Encontrar algo siempre demuestra que existe, incluso con el arbol
    truncado. No encontrarlo solo demuestra su ausencia si hemos podido mirar
    el arbol entero; si no, la respuesta honesta es null.
    """
    if encontrados:
        return QualitySignal(detected=True, files=sorted(set(encontrados)))
    if not available or truncated:
        return QualitySignal(detected=None, files=[])
    return QualitySignal(detected=False, files=[])


def _flag(encontrado: bool, *, available: bool, truncated: bool) -> bool | None:
    """Como _signal, pero para un booleano suelto."""
    if encontrado:
        return True
    if not available or truncated:
        return None
    return False


def analyze_quality(
    paths: Iterable[str], *, available: bool = True, truncated: bool = False
) -> Quality:
    """Deduce las senales de calidad de una lista de rutas de archivo.

    Args:
        paths: rutas de los archivos del repositorio, relativas a la raiz.
        available: False si no hemos podido obtener el arbol. Entonces no se
            afirma nada: todas las senales quedan en null.
        truncated: True si GitHub corto el arbol por tamano. Entonces una
            ausencia no demuestra nada y tambien se publica como null.
    """
    rutas = [path.lower() for path in paths] if available else []

    tests = [ruta for ruta in rutas if _is_test(ruta)]
    directorios = sorted({d for ruta in tests if (d := _test_directory(ruta))})

    ci = [
        ruta
        for ruta in rutas
        if _is_workflow(ruta) or _is_circleci(ruta) or _basename(ruta) in CI_FILES
    ]
    linting = [r for r in rutas if _matches(_basename(r), LINTER_FILES, LINTER_PATTERNS)]
    formatting = [
        r for r in rutas if _matches(_basename(r), FORMATTER_FILES, FORMATTER_PATTERNS)
    ]
    typing_ = [r for r in rutas if _basename(r) in TYPE_FILES]
    dependencies = [
        r for r in rutas if _matches(_basename(r), DEPENDENCY_FILES, DEPENDENCY_PATTERNS)
    ]
    coverage = [r for r in rutas if _basename(r) in COVERAGE_FILES]

    readme = [r for r in rutas if _basename(r) in README]
    contributing = [r for r in rutas if _basename(r) in CONTRIBUTING]
    docs = [r for r in rutas if r.startswith("docs/")]

    return Quality(
        tree_available=available,
        tree_truncated=truncated,
        files_scanned=len(rutas),
        tests=TestsSignal(
            detected=_flag(bool(tests), available=available, truncated=truncated),
            files=len(tests),
            directories=directorios,
        ),
        documentation=DocumentationSignal(
            readme=_flag(bool(readme), available=available, truncated=truncated),
            contributing=_flag(
                bool(contributing), available=available, truncated=truncated
            ),
            docs_directory=_flag(bool(docs), available=available, truncated=truncated),
            files=sorted(set(readme + contributing)),
        ),
        ci=_signal(ci, available=available, truncated=truncated),
        linting=_signal(linting, available=available, truncated=truncated),
        formatting=_signal(formatting, available=available, truncated=truncated),
        type_checking=_signal(typing_, available=available, truncated=truncated),
        dependencies=_signal(dependencies, available=available, truncated=truncated),
        coverage=CoverageSignal(
            configured=_flag(bool(coverage), available=available, truncated=truncated),
            # Nunca se rellena: saber el porcentaje exigiria ejecutar la suite
            # del repositorio analizado, que es justo lo que no hacemos.
            percentage=None,
            files=sorted(set(coverage)),
        ),
        undetermined_config=sorted(
            {r for r in rutas if _basename(r) in UNDETERMINED_FILES}
        ),
    )
