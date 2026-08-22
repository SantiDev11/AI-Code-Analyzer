"""Tests para la funcionalidad de Code Metrics."""

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import github
from tests.conftest import (
    REPO_PAYLOAD,
    TREE_PAYLOAD,
    is_repository_endpoint,
    successful_handler,
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


async def test_metrics_repositorio_con_archivos(fake_github):
    """Calcula metricas basicas en un repositorio normal."""
    fake_github(successful_handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.metrics.tree_available is True
    assert result.metrics.tree_truncated is False
    assert result.metrics.total_files == len(TREE_PAYLOAD["tree"])
    assert result.metrics.total_directories >= 2
    assert result.metrics.test_files == 1  # tests/test_client.py
    assert result.metrics.documentation_files == 2  # README.md, CONTRIBUTING.md
    assert result.metrics.lines_of_code is None


async def test_metrics_repositorio_vacio(fake_github):
    """En un repositorio vacio (0 archivos), los recuentos son 0 y LOC es None."""
    def handler(request: httpx.Request) -> httpx.Response:
        if "/git/trees/" in request.url.path:
            return httpx.Response(200, json={"tree": [], "truncated": False})
        return successful_handler(request)

    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    metrics = result.metrics
    assert metrics.tree_available is True
    assert metrics.tree_truncated is False
    assert metrics.total_files == 0
    assert metrics.total_directories == 0
    assert metrics.source_files == 0
    assert metrics.test_files == 0
    assert metrics.documentation_files == 0
    assert metrics.configuration_files == 0
    assert metrics.file_extensions == {}
    assert metrics.largest_files == []
    assert metrics.lines_of_code is None


async def test_metrics_conteo_total_de_archivos_y_directorios(fake_github):
    """Verifica conteo exacto de archivos y deduccion jerarquica de directorios."""
    custom_tree = {
        "tree": [
            {"path": "src/app/main.py", "type": "blob", "size": 100},
            {"path": "src/app/utils.py", "type": "blob", "size": 200},
            {"path": "tests/unit/test_main.py", "type": "blob", "size": 300},
            {"path": "README.md", "type": "blob", "size": 400},
        ],
        "truncated": False,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        if "/git/trees/" in request.url.path:
            return httpx.Response(200, json=custom_tree)
        return successful_handler(request)

    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.metrics.total_files == 4
    # Directorios: src, src/app, tests, tests/unit -> 4
    assert result.metrics.total_directories == 4


async def test_metrics_archivos_por_extension(fake_github):
    """Agrupa y normaliza extensiones de archivos."""
    custom_tree = {
        "tree": [
            {"path": "main.py", "type": "blob"},
            {"path": "utils.PY", "type": "blob"},  # Mayuscula normalizada a minuscula
            {"path": "README.md", "type": "blob"},
            {"path": "config.json", "type": "blob"},
        ],
        "truncated": False,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        if "/git/trees/" in request.url.path:
            return httpx.Response(200, json=custom_tree)
        return successful_handler(request)

    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    extensions = result.metrics.file_extensions
    assert extensions[".py"] == 2
    assert extensions[".md"] == 1
    assert extensions[".json"] == 1


async def test_metrics_archivos_sin_extension(fake_github):
    """Maneja correctamente archivos sin extension como Dockerfile, Makefile o LICENSE."""
    custom_tree = {
        "tree": [
            {"path": "Dockerfile", "type": "blob"},
            {"path": "Makefile", "type": "blob"},
            {"path": "LICENSE", "type": "blob"},
            {"path": ".gitignore", "type": "blob"},
            {"path": "main.go", "type": "blob"},
        ],
        "truncated": False,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        if "/git/trees/" in request.url.path:
            return httpx.Response(200, json=custom_tree)
        return successful_handler(request)

    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    extensions = result.metrics.file_extensions
    assert extensions.get("") == 4  # Dockerfile, Makefile, LICENSE, .gitignore
    assert extensions.get(".go") == 1


async def test_metrics_distingue_source_test_doc_config(fake_github):
    """Distingue codigo fuente, tests, documentacion y configuracion."""
    custom_tree = {
        "tree": [
            {"path": "app/main.py", "type": "blob"},  # Source
            {"path": "app/service.py", "type": "blob"},  # Source
            {"path": "tests/test_main.py", "type": "blob"},  # Test
            {"path": "app/feature_test.py", "type": "blob"},  # Test
            {"path": "README.md", "type": "blob"},  # Doc
            {"path": "docs/architecture.md", "type": "blob"},  # Doc
            {"path": "pyproject.toml", "type": "blob"},  # Config
            {"path": ".github/workflows/ci.yml", "type": "blob"},  # Config
            {"path": "Dockerfile", "type": "blob"},  # Config
        ],
        "truncated": False,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        if "/git/trees/" in request.url.path:
            return httpx.Response(200, json=custom_tree)
        return successful_handler(request)

    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    metrics = result.metrics
    assert metrics.source_files == 2
    assert metrics.test_files == 2
    assert metrics.documentation_files == 2
    assert metrics.configuration_files == 3


async def test_metrics_largest_files_y_orden(fake_github):
    """Calcula y ordena los archivos mas grandes en orden descendente por size_bytes."""
    custom_tree = {
        "tree": [
            {"path": "small.py", "type": "blob", "size": 100},
            {"path": "huge.bin", "type": "blob", "size": 100000},
            {"path": "medium.js", "type": "blob", "size": 5000},
            {"path": "large.py", "type": "blob", "size": 25000},
            {"path": "no_size.txt", "type": "blob"},  # Sin size
        ],
        "truncated": False,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        if "/git/trees/" in request.url.path:
            return httpx.Response(200, json=custom_tree)
        return successful_handler(request)

    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    largest = result.metrics.largest_files
    assert len(largest) == 4
    assert largest[0].path == "huge.bin"
    assert largest[0].size_bytes == 100000
    assert largest[1].path == "large.py"
    assert largest[1].size_bytes == 25000
    assert largest[2].path == "medium.js"
    assert largest[2].size_bytes == 5000
    assert largest[3].path == "small.py"
    assert largest[3].size_bytes == 100


async def test_metrics_lines_of_code_siempre_null(fake_github):
    """Lineas de codigo no se inventan desde Git Tree y permanece null."""
    fake_github(successful_handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.metrics.lines_of_code is None


async def test_metrics_repositorio_multilenguaje(fake_github):
    """Detecta multiples lenguajes de codigo fuente."""
    custom_tree = {
        "tree": [
            {"path": "backend/main.go", "type": "blob"},
            {"path": "backend/util.rs", "type": "blob"},
            {"path": "frontend/app.tsx", "type": "blob"},
            {"path": "frontend/styles.css", "type": "blob"},
            {"path": "scripts/build.sh", "type": "blob"},
        ],
        "truncated": False,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        if "/git/trees/" in request.url.path:
            return httpx.Response(200, json=custom_tree)
        return successful_handler(request)

    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.metrics.source_files == 5
    assert result.metrics.file_extensions[".go"] == 1
    assert result.metrics.file_extensions[".rs"] == 1
    assert result.metrics.file_extensions[".tsx"] == 1
    assert result.metrics.file_extensions[".css"] == 1
    assert result.metrics.file_extensions[".sh"] == 1


async def test_metrics_tree_truncado(fake_github):
    """Cuando el tree es truncado, tree_truncated se marca en True."""
    custom_tree = {
        "tree": [
            {"path": "main.py", "type": "blob", "size": 500},
        ],
        "truncated": True,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        if "/git/trees/" in request.url.path:
            return httpx.Response(200, json=custom_tree)
        return successful_handler(request)

    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.metrics.tree_available is True
    assert result.metrics.tree_truncated is True
    assert result.metrics.total_files == 1
    assert result.metrics.source_files == 1


async def test_metrics_error_endpoint_tree_degrada_con_tree_unavailable(fake_github):
    """Si el endpoint tree falla (500), tree_available es False y totales son 0."""
    def handler(request: httpx.Request) -> httpx.Response:
        if "/git/trees/" in request.url.path:
            return httpx.Response(500, json={"message": "Server Error"})
        return successful_handler(request)

    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert result.metrics.tree_available is False
    assert result.metrics.tree_truncated is False
    assert result.metrics.total_files == 0
    assert result.metrics.lines_of_code is None


async def test_metrics_repositorio_inexistente_lanza_not_found(fake_github):
    """Un repositorio inexistente lanza RepositoryNotFound."""
    fake_github(lambda request: httpx.Response(404, json={"message": "Not Found"}))

    with pytest.raises(github.RepositoryNotFound):
        await github.analyze_repository("no-owner", "no-repo")


def test_metrics_integracion_endpoint_http(client, fake_github):
    """GET /analyze/{owner}/{repo} incluye metrics en la respuesta HTTP."""
    fake_github(successful_handler)

    response = client.get("/analyze/encode/httpx")

    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "total_files" in data["metrics"]
    assert "file_extensions" in data["metrics"]
    assert "largest_files" in data["metrics"]
    assert data["metrics"]["lines_of_code"] is None


async def test_metrics_y_quality_reutilizan_mismo_tree(fake_github):
    """Ambas funciones coexisten y se calculan a partir de una unica llamada al Git Tree."""
    tree_calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        if "/git/trees/" in request.url.path:
            tree_calls.append(request.url.path)
            return httpx.Response(200, json=TREE_PAYLOAD)
        return successful_handler(request)

    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert len(tree_calls) == 1, "solo se debe consultar el Git Tree una vez"
    assert result.quality.tree_available is True
    assert result.metrics.tree_available is True
