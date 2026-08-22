"""Tests de la capa HTTP: cada error del servicio debe dar el codigo correcto."""

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import successful_handler


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_devuelve_la_estructura_esperada(client, fake_github):
    fake_github(successful_handler)

    response = client.get("/analyze/encode/httpx")

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "repository",
        "languages",
        "contributors_count",
        "latest_release",
        "recent_commits",
        "cached",
    }
    assert set(body["repository"]) == {
        "name",
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
    }
    assert body["contributors_count"] == 247


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
