"""Tests para la integracion de Git Tree y Code Quality."""

import httpx
import pytest

from app.services import github
from tests.conftest import (
    REPO_PAYLOAD,
    TREE_PAYLOAD,
    is_repository_endpoint,
    successful_handler,
)


async def test_quality_con_default_branch_main(fake_github):
    """Consulta /git/trees/main cuando default_branch es main."""
    consulted_paths = []

    def handler(request: httpx.Request) -> httpx.Response:
        consulted_paths.append(request.url.path)
        if is_repository_endpoint(request):
            return httpx.Response(
                200, json={**REPO_PAYLOAD, "default_branch": "main"}
            )
        if request.url.path.endswith("/git/trees/main"):
            return httpx.Response(200, json=TREE_PAYLOAD)
        return successful_handler(request)

    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert "/repos/encode/httpx/git/trees/main" in consulted_paths
    assert result.repository.default_branch == "main"
    assert result.quality.tree_available is True
    assert result.quality.tests.detected is True


async def test_quality_con_default_branch_master(fake_github):
    """Consulta /git/trees/master cuando default_branch es master."""
    consulted_paths = []

    def handler(request: httpx.Request) -> httpx.Response:
        consulted_paths.append(request.url.path)
        if is_repository_endpoint(request):
            return httpx.Response(
                200, json={**REPO_PAYLOAD, "default_branch": "master"}
            )
        if request.url.path.endswith("/git/trees/master"):
            return httpx.Response(200, json=TREE_PAYLOAD)
        return successful_handler(request)

    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert "/repos/encode/httpx/git/trees/master" in consulted_paths
    assert result.repository.default_branch == "master"
    assert result.quality.tree_available is True
    assert result.quality.documentation.readme is True


async def test_quality_con_otra_rama_por_defecto(fake_github):
    """Consulta /git/trees/develop cuando default_branch es develop."""
    consulted_paths = []

    def handler(request: httpx.Request) -> httpx.Response:
        consulted_paths.append(request.url.path)
        if is_repository_endpoint(request):
            return httpx.Response(
                200, json={**REPO_PAYLOAD, "default_branch": "develop"}
            )
        if request.url.path.endswith("/git/trees/develop"):
            return httpx.Response(200, json=TREE_PAYLOAD)
        return successful_handler(request)

    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    assert "/repos/encode/httpx/git/trees/develop" in consulted_paths
    assert result.repository.default_branch == "develop"
    assert result.quality.tree_available is True


async def test_quality_tree_exitoso_y_senales(fake_github):
    """Verifica que el tree exitoso extrae todas las senales de calidad."""
    custom_tree = {
        "sha": "tree123",
        "url": "https://api.github.com/...",
        "tree": [
            {"path": "README.md", "type": "blob"},
            {"path": "CONTRIBUTING.rst", "type": "blob"},
            {"path": "docs/index.md", "type": "blob"},
            {"path": "tests/test_api.py", "type": "blob"},
            {"path": "src/test/java/AppTest.java", "type": "blob"},
            {"path": ".github/workflows/ci.yml", "type": "blob"},
            {"path": ".flake8", "type": "blob"},
            {"path": "ruff.toml", "type": "blob"},
            {"path": ".editorconfig", "type": "blob"},
            {"path": "mypy.ini", "type": "blob"},
            {"path": "pyproject.toml", "type": "blob"},
            {"path": ".coveragerc", "type": "blob"},
        ],
        "truncated": False,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        if "/git/trees/" in request.url.path:
            return httpx.Response(200, json=custom_tree)
        return successful_handler(request)

    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    quality = result.quality
    assert quality.tree_available is True
    assert quality.tree_truncated is False
    assert quality.files_scanned == 12

    # Tests
    assert quality.tests.detected is True
    assert quality.tests.files == 2
    assert "tests" in quality.tests.directories
    assert "src/test" in quality.tests.directories

    # Documentation
    assert quality.documentation.readme is True
    assert quality.documentation.contributing is True
    assert quality.documentation.docs_directory is True

    # Signals
    assert quality.ci.detected is True
    assert ".github/workflows/ci.yml" in quality.ci.files
    assert quality.linting.detected is True
    assert ".flake8" in quality.linting.files
    assert quality.formatting.detected is True
    assert ".editorconfig" in quality.formatting.files
    assert quality.type_checking.detected is True
    assert "mypy.ini" in quality.type_checking.files
    assert quality.dependencies.detected is True
    assert "pyproject.toml" in quality.dependencies.files
    assert quality.coverage.configured is True
    assert ".coveragerc" in quality.coverage.files
    assert quality.coverage.percentage is None
    assert "pyproject.toml" in quality.undetermined_config


async def test_quality_tree_vacio(fake_github):
    """Un repositorio con arbol vacio responde con senales en False."""
    def handler(request: httpx.Request) -> httpx.Response:
        if "/git/trees/" in request.url.path:
            return httpx.Response(200, json={"tree": [], "truncated": False})
        return successful_handler(request)

    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    quality = result.quality
    assert quality.tree_available is True
    assert quality.tree_truncated is False
    assert quality.files_scanned == 0
    assert quality.tests.detected is False
    assert quality.tests.files == 0
    assert quality.documentation.readme is False
    assert quality.documentation.contributing is False
    assert quality.documentation.docs_directory is False
    assert quality.ci.detected is False
    assert quality.linting.detected is False
    assert quality.formatting.detected is False
    assert quality.type_checking.detected is False
    assert quality.dependencies.detected is False
    assert quality.coverage.configured is False
    assert quality.undetermined_config == []


async def test_repositorio_inexistente_mantiene_not_found(fake_github):
    """Si el repositorio no existe (404 en metadata), lanza RepositoryNotFound."""
    fake_github(lambda request: httpx.Response(404, json={"message": "Not Found"}))

    with pytest.raises(github.RepositoryNotFound):
        await github.analyze_repository("no-owner", "no-repo")


async def test_error_endpoint_tree_degrada_con_tree_unavailable(fake_github):
    """Si el endpoint de tree falla (ej. 500 o 404 en tree), tree_available es False y las senales son None."""
    def handler(request: httpx.Request) -> httpx.Response:
        if "/git/trees/" in request.url.path:
            return httpx.Response(500, json={"message": "Internal Server Error"})
        return successful_handler(request)

    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    quality = result.quality
    assert quality.tree_available is False
    assert quality.tree_truncated is False
    assert quality.files_scanned == 0
    assert quality.tests.detected is None
    assert quality.documentation.readme is None
    assert quality.ci.detected is None
    assert quality.linting.detected is None
    assert quality.formatting.detected is None
    assert quality.type_checking.detected is None
    assert quality.dependencies.detected is None
    assert quality.coverage.configured is None


async def test_tree_404_o_409_degrada_con_tree_unavailable(fake_github):
    """Si el tree devuelve 404 o 409 (ej. repo recien creado sin arbol git), tree_available es False."""
    def handler(request: httpx.Request) -> httpx.Response:
        if "/git/trees/" in request.url.path:
            return httpx.Response(409, json={"message": "Git Repository is empty."})
        return successful_handler(request)

    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    quality = result.quality
    assert quality.tree_available is False
    assert quality.tests.detected is None


async def test_tree_truncado_publica_ausencias_como_none(fake_github):
    """Si GitHub trunca el arbol, las ausencias son None y los hallazgos son True."""
    custom_tree = {
        "tree": [
            {"path": "README.md", "type": "blob"},
            {"path": ".flake8", "type": "blob"},
        ],
        "truncated": True,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        if "/git/trees/" in request.url.path:
            return httpx.Response(200, json=custom_tree)
        return successful_handler(request)

    fake_github(handler)

    result = await github.analyze_repository("encode", "httpx")

    quality = result.quality
    assert quality.tree_available is True
    assert quality.tree_truncated is True
    # Encontrados son True
    assert quality.documentation.readme is True
    assert quality.linting.detected is True
    # No encontrados son None por truncado
    assert quality.tests.detected is None
    assert quality.formatting.detected is None
    assert quality.type_checking.detected is None
    assert quality.coverage.configured is None
