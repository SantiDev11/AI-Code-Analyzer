"""Tests para el contrato publico de la API, esquemas OpenAPI y consistencia de documentacion."""

import re
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.schemas.repository import (
    Activity,
    AIAnalysis,
    AnalysisResponse,
    Commit,
    Concern,
    Contributor,
    CoverageSignal,
    DailyActivity,
    DocumentationSignal,
    Issue,
    LargeFile,
    Metrics,
    PullRequest,
    Quality,
    QualitySignal,
    Recommendation,
    Release,
    ReleaseDetail,
    Repository,
    TechnicalOverview,
    TestsSignal,
)
from tests.conftest import successful_handler
from tests.test_ai_analysis import VALID_AI_RESPONSE_PAYLOAD, ai_success_handler


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_openapi_schema_generates_successfully(client):
    """Verifica que /openapi.json se genera correctamente con los endpoints y schemas esperados."""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    openapi = response.json()
    assert openapi["info"]["title"] == "AI-Code-Analyzer"
    assert "/analyze/{owner}/{repo}" in openapi["paths"]
    assert "/health" in openapi["paths"]

    # Endpoint GET /analyze/{owner}/{repo}
    analyze_op = openapi["paths"]["/analyze/{owner}/{repo}"]["get"]
    assert analyze_op["summary"] == "Analiza un repositorio publico de GitHub"

    # Parametros de consulta
    param_names = [p["name"] for p in analyze_op["parameters"]]
    assert "owner" in param_names
    assert "repo" in param_names
    assert "commits" in param_names
    assert "issues" in param_names
    assert "pulls" in param_names
    assert "releases" in param_names
    assert "activity_days" in param_names

    # Componentes / Schemas
    schemas = openapi["components"]["schemas"]
    assert "AnalysisResponse" in schemas
    assert "Repository" in schemas
    assert "Activity" in schemas
    assert "Quality" in schemas
    assert "Metrics" in schemas
    assert "AIAnalysis" in schemas
    assert "Concern" in schemas
    assert "Recommendation" in schemas
    assert "TechnicalOverview" in schemas


def test_analysis_response_schema_fields():
    """Verifica que el schema Pydantic AnalysisResponse contiene todos los campos del contrato."""
    fields = AnalysisResponse.model_fields
    expected_fields = {
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
    assert set(fields.keys()) == expected_fields


def test_ai_analysis_schema_fields():
    """Verifica los campos obligatorios del modelo AIAnalysis y submodelos."""
    ai_fields = AIAnalysis.model_fields
    assert set(ai_fields.keys()) == {
        "summary",
        "strengths",
        "concerns",
        "recommendations",
        "technical_overview",
    }

    concern_fields = Concern.model_fields
    assert set(concern_fields.keys()) == {"title", "description", "severity", "evidence"}

    rec_fields = Recommendation.model_fields
    assert set(rec_fields.keys()) == {"title", "description", "priority"}

    tech_fields = TechnicalOverview.model_fields
    assert set(tech_fields.keys()) == {"architecture", "stack", "activity_summary"}


def test_analyze_contract_without_ai_key(client, fake_github, monkeypatch):
    """Sin AI_API_KEY, ai_analysis es null y el contrato es 100% valido."""
    monkeypatch.setattr(settings, "ai_api_key", None)
    fake_github(successful_handler)

    response = client.get("/analyze/encode/httpx")
    assert response.status_code == 200

    data = response.json()
    assert data["ai_analysis"] is None
    assert data["quality"]["tree_available"] is True
    assert data["metrics"]["tree_available"] is True
    assert data["cached"] is False

    # Validable directamente con el modelo Pydantic
    parsed = AnalysisResponse.model_validate(data)
    assert parsed.ai_analysis is None


def test_analyze_contract_with_mocked_ai(client, fake_github, monkeypatch):
    """Con AI_API_KEY y mock exitoso, ai_analysis cumple estrictamente el esquema."""
    monkeypatch.setattr(settings, "ai_api_key", "sk-mock-key")

    from app.services.ai import client as ai_client_module

    def compound_handler(request: httpx.Request) -> httpx.Response:
        if "/chat/completions" in request.url.path:
            return ai_success_handler(request)
        return successful_handler(request)

    fake_github(compound_handler)
    monkeypatch.setattr(
        ai_client_module,
        "_create_ai_client",
        lambda: httpx.AsyncClient(transport=httpx.MockTransport(compound_handler)),
    )

    response = client.get("/analyze/encode/httpx")
    assert response.status_code == 200

    data = response.json()
    assert data["ai_analysis"] is not None
    parsed = AnalysisResponse.model_validate(data)
    assert parsed.ai_analysis is not None
    assert parsed.ai_analysis.summary == VALID_AI_RESPONSE_PAYLOAD["summary"]
    assert len(parsed.ai_analysis.concerns) == 1
    assert parsed.ai_analysis.concerns[0].severity in ("low", "medium", "high")
    assert parsed.ai_analysis.recommendations[0].priority in ("low", "medium", "high")


def test_readme_does_not_contain_real_secrets():
    """Verifica que README.md no contenga tokens reales de GitHub o OpenAI."""
    readme_path = Path(__file__).parent.parent / "README.md"
    content = readme_path.read_text(encoding="utf-8")

    # Tokens clasicos o fine-grained de GitHub
    assert not re.search(r"ghp_[a-zA-Z0-9]{30,}", content)
    assert not re.search(r"github_pat_[a-zA-Z0-9]{22,}", content)

    # Tokens de OpenAI
    assert not re.search(r"sk-[a-zA-Z0-9]{20,}", content)
