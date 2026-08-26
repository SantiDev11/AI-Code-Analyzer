"""Tests de la capa HTTP: cada error del servicio debe dar el codigo correcto."""

import re
from urllib.parse import urljoin

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import STATIC_DIR, app
from tests.conftest import successful_handler


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_la_interfaz_web_se_sirve_en_la_raiz(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_la_hoja_de_estilos_enlazada_se_sirve(client):
    """Pide la ruta que enlaza el HTML, no una que demos por supuesta.

    Comprueba que los estilos referenciados en index.html se sirvan con
    codigo 200 y content-type text/css.
    """
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    href = re.search(r'<link rel="stylesheet"[^>]*href="([^"]+)"', html).group(1)

    response = client.get(urljoin("/", href))

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/css")


def test_docs_y_openapi_disponibles(client):
    """Verifica que Swagger UI, ReDoc y OpenAPI sigan disponibles."""
    docs_resp = client.get("/docs")
    assert docs_resp.status_code == 200

    openapi_resp = client.get("/openapi.json")
    assert openapi_resp.status_code == 200
    assert "paths" in openapi_resp.json()


def test_spa_fallback_para_rutas_desconocidas(client):
    """Las rutas no-API deben devolver index.html para routing de cliente SPA."""
    response = client.get("/cualquier/ruta/frontend")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "AI-Code-Analyzer" in response.text


def test_sin_secretos_en_frontend_dist():
    """Verifica que ningun secreto del backend quede en los archivos estaticos."""
    if not STATIC_DIR.exists():
        return

    for file_path in STATIC_DIR.rglob("*"):
        if file_path.is_file() and file_path.suffix in {".js", ".html", ".css", ".map"}:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            assert "AI_API_KEY" not in content
            assert "GITHUB_TOKEN" not in content


def test_analyze_devuelve_la_estructura_esperada(client, fake_github):
    fake_github(successful_handler)

    response = client.get("/analyze/encode/httpx")

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "repository",
        "languages",
        "contributors",
        "contributors_count",
        "latest_release",
        "recent_commits",
        "issues",
        "issues_count",
        "open_issues_count",
        "closed_issues_count",
        "pull_requests",
        "pull_requests_count",
        "open_pull_requests_count",
        "closed_pull_requests_count",
        "merged_pull_requests_count",
        "releases",
        "releases_count",
        "published_releases_count",
        "draft_releases_count",
        "prereleases_count",
        "activity",
        "quality",
        "metrics",
        "ai_analysis",
        "cached",
    }
    assert set(body["repository"]) == {
        "name",
        "full_name",
        "description",
        "stars",
        "forks",
        "open_issues",
        "created_at",
        "updated_at",
        "primary_language",
        "url",
        "license",
        "topics",
        "size_kb",
        "is_archived",
        "default_branch",
    }
    assert body["contributors_count"] == len(body["contributors"])


def test_repositorio_inexistente_devuelve_404(client, fake_github):
    fake_github(lambda request: httpx.Response(404, json={"message": "Not Found"}))

    response = client.get("/analyze/SantiDev11/no-existe")

    assert response.status_code == 404
    assert "no encontrado" in response.json()["detail"]


def test_cuota_agotada_devuelve_429(client, fake_github):
    fake_github(
        lambda request: httpx.Response(
            403, json={"message": "rate limit"}, headers={"X-RateLimit-Remaining": "0"}
        )
    )

    response = client.get("/analyze/encode/httpx")

    assert response.status_code == 429


def test_error_inesperado_de_github_devuelve_502(client, fake_github):
    fake_github(lambda request: httpx.Response(500, json={"message": "boom"}))

    response = client.get("/analyze/encode/httpx")

    assert response.status_code == 502
