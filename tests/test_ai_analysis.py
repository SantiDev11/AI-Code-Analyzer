"""Tests para la funcionalidad de AI Analysis."""

import json
from datetime import UTC, datetime

import httpx
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.schemas.repository import (
    Activity,
    AIAnalysis,
    Commit,
    Contributor,
    CoverageSignal,
    DocumentationSignal,
    Issue,
    LargeFile,
    Metrics,
    PullRequest,
    Quality,
    QualitySignal,
    Release,
    ReleaseDetail,
    Repository,
    TestsSignal,
)
from app.services import github
from app.services.ai import client as ai_client_module
from app.services.ai import exceptions as ai_exceptions
from app.services.ai import service as ai_service
from app.services.ai.client import complete_chat
from app.services.ai.context import build_ai_context
from app.services.ai.service import analyze_with_ai, run_ai_analysis
from tests.conftest import REPO_PAYLOAD, TREE_PAYLOAD, successful_handler

VALID_AI_RESPONSE_PAYLOAD = {
    "summary": "Proyecto bien estructurado y con mantenimiento constante.",
    "strengths": [
        "Suite de tests configurada con cobertura de casos principales.",
        "Documentacion completa incluyendo README y guia de contribucion.",
    ],
    "concerns": [
        {
            "title": "Dependencias sin archivo de bloqueo explicito",
            "description": "No se identifico poetry.lock o Pipfile.lock.",
            "severity": "medium",
            "evidence": "1 archivo pyproject.toml detectado sin lockfile correspondiente.",
        }
    ],
    "recommendations": [
        {
            "title": "Agregar comprobacion de tipos estricta",
            "description": "Incorporar mypy en el workflow de CI para prevenir errores de tipado.",
            "priority": "high",
        }
    ],
    "technical_overview": {
        "architecture": "Arquitectura modular en capas con separacion de servicios y esquemas.",
        "stack": "Python, FastAPI, Pydantic, pytest.",
        "activity_summary": "Actividad reciente regular con commits y resolucion de issues.",
    },
}


def create_sample_repository_data():
    """Genera datos de prueba para construir el contexto."""
    now = datetime(2026, 8, 22, 12, 0, 0, tzinfo=UTC)

    repo = Repository(
        name="httpx",
        full_name="encode/httpx",
        description="A next generation HTTP client for Python.",
        stars=15000,
        forks=1200,
        open_issues=15,
        created_at=now,
        updated_at=now,
        primary_language="Python",
        url="https://github.com/encode/httpx",
        license="BSD-3-Clause",
        topics=["http", "asyncio"],
        size_kb=8500,
        is_archived=False,
        default_branch="master",
    )

    languages = {"Python": 500000, "Shell": 2500}

    contributors = [
        Contributor(
            username=f"user_{i}",
            contributions=100 - i,
            avatar_url="https://avatar.url",
            profile_url="https://profile.url",
        )
        for i in range(10)
    ]

    commits = [
        Commit(
            sha=f"sha_{i}",
            message=f"Commit message {i}",
            author=f"author_{i}",
            date=now,
            url="https://commit.url",
        )
        for i in range(10)
    ]

    issues = [
        Issue(
            number=i,
            title=f"Issue title {i}",
            state="open" if i % 2 == 0 else "closed",
            author=f"author_{i}",
            created_at=now,
            updated_at=now,
            url="https://issue.url",
        )
        for i in range(10)
    ]

    pull_requests = [
        PullRequest(
            number=100 + i,
            title=f"PR title {i}",
            state="open" if i % 2 == 0 else "closed",
            author=f"author_{i}",
            created_at=now,
            updated_at=now,
            closed_at=now if i % 2 != 0 else None,
            merged_at=now if i % 2 != 0 else None,
            source_branch="feat",
            target_branch="master",
            url="https://pr.url",
        )
        for i in range(10)
    ]

    releases = [
        ReleaseDetail(
            id=i,
            tag_name=f"v1.{i}.0",
            name=f"Release 1.{i}",
            body="Notes",
            draft=False,
            prerelease=False,
            created_at=now,
            published_at=now,
            author="author",
            url="https://release.url",
        )
        for i in range(10)
    ]

    latest_release = Release(
        tag="v1.9.0",
        name="Release 1.9",
        published_at=now,
        url="https://release.url",
    )

    activity = Activity(
        days=30,
        since=now.date(),
        until=now.date(),
        total_commits=10,
        total_issues=10,
        total_pull_requests=10,
        total_releases=10,
        daily=[],
    )

    quality = Quality(
        tree_available=True,
        tree_truncated=False,
        files_scanned=25,
        tests=TestsSignal(detected=True, files=5, directories=["tests"]),
        documentation=DocumentationSignal(
            readme=True, contributing=True, docs_directory=True, files=["README.md"]
        ),
        ci=QualitySignal(detected=True, files=[".github/workflows/ci.yml"]),
        linting=QualitySignal(detected=True, files=[".flake8"]),
        formatting=QualitySignal(detected=True, files=[".editorconfig"]),
        type_checking=QualitySignal(detected=True, files=["mypy.ini"]),
        dependencies=QualitySignal(detected=True, files=["pyproject.toml"]),
        coverage=CoverageSignal(configured=None, percentage=None, files=[]),
        undetermined_config=["pyproject.toml"],
    )

    metrics = Metrics(
        tree_available=True,
        tree_truncated=False,
        total_files=25,
        total_directories=5,
        source_files=15,
        test_files=5,
        documentation_files=2,
        configuration_files=3,
        file_extensions={
            ".py": 18,
            ".md": 2,
            ".toml": 2,
            ".yml": 2,
            ".ini": 1,
            ".txt": 1,
            ".json": 1,
        },
        largest_files=[
            LargeFile(path=f"file_{i}.py", size_bytes=1000 * (10 - i))
            for i in range(10)
        ],
        lines_of_code=None,
    )

    return (
        repo,
        languages,
        contributors,
        commits,
        issues,
        pull_requests,
        releases,
        latest_release,
        activity,
        quality,
        metrics,
    )


@pytest.fixture
def fake_ai_client(monkeypatch):
    """Instala un cliente de IA simulado con httpx.MockTransport."""
    def install(handler):
        def create_client():
            return httpx.AsyncClient(
                transport=httpx.MockTransport(handler),
                timeout=httpx.Timeout(5.0),
            )

        monkeypatch.setattr(ai_client_module, "_create_ai_client", create_client)

    return install


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def ai_success_handler(request: httpx.Request) -> httpx.Response:
    """Responde exitosamente con un chat completion OpenAI-compatible."""
    return httpx.Response(
        200,
        json={
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": json.dumps(VALID_AI_RESPONSE_PAYLOAD),
                    },
                    "finish_reason": "stop",
                }
            ],
        },
    )


# --------------------------------------------------------------------------
# Tests de Context Builder y Limites
# --------------------------------------------------------------------------


def test_context_builder_limita_items_y_no_incluye_secretos(monkeypatch):
    """Verifica limites de 5 elementos y ausencia absoluta de tokens o claves."""
    monkeypatch.setattr(settings, "github_token", "ghp_super_secret_github_token")
    monkeypatch.setattr(settings, "ai_api_key", "sk-super_secret_ai_key")

    (
        repo,
        languages,
        contributors,
        commits,
        issues,
        pull_requests,
        releases,
        latest_release,
        activity,
        quality,
        metrics,
    ) = create_sample_repository_data()

    context = build_ai_context(
        repo,
        languages,
        contributors,
        commits,
        issues,
        pull_requests,
        releases,
        latest_release,
        activity,
        quality,
        metrics,
    )

    # Limites
    assert len(context["contributors"]["sampled_top"]) == 5
    assert len(context["recent_commits"]["sampled"]) == 5
    assert len(context["issues"]["sampled"]) == 5
    assert len(context["pull_requests"]["sampled"]) == 5
    assert len(context["metrics"]["top_file_extensions"]) == 5
    assert len(context["metrics"]["top_largest_files"]) == 5

    # LOC y Coverage
    assert context["metrics"]["lines_of_code"] is None
    assert context["quality"]["coverage"]["configured"] is None

    # Serializacion y ausencia de secretos
    serialized = json.dumps(context)
    assert "ghp_super_secret_github_token" not in serialized
    assert "sk-super_secret_ai_key" not in serialized
    assert "authorization" not in serialized.lower()


def test_context_builder_tree_truncado():
    """tree_truncated se propaga correctamente al contexto."""
    (
        repo,
        languages,
        contributors,
        commits,
        issues,
        pull_requests,
        releases,
        latest_release,
        activity,
        quality,
        metrics,
    ) = create_sample_repository_data()

    quality_trunc = quality.model_copy(update={"tree_truncated": True})
    metrics_trunc = metrics.model_copy(update={"tree_truncated": True})

    context = build_ai_context(
        repo,
        languages,
        contributors,
        commits,
        issues,
        pull_requests,
        releases,
        latest_release,
        activity,
        quality_trunc,
        metrics_trunc,
    )

    assert context["quality"]["tree_truncated"] is True
    assert context["metrics"]["tree_truncated"] is True


# --------------------------------------------------------------------------
# Tests de Cliente y Servicio de IA (Manejo de Errores y Validacion)
# --------------------------------------------------------------------------


async def test_ai_analysis_exitoso_y_validado(fake_ai_client):
    """Prueba el flujo completo exitoso con respuesta valida parseada a AIAnalysis."""
    fake_ai_client(ai_success_handler)

    (
        repo,
        languages,
        contributors,
        commits,
        issues,
        pull_requests,
        releases,
        latest_release,
        activity,
        quality,
        metrics,
    ) = create_sample_repository_data()

    result = await run_ai_analysis(
        repo,
        languages,
        contributors,
        commits,
        issues,
        pull_requests,
        releases,
        latest_release,
        activity,
        quality,
        metrics,
        api_key="sk-test-key",
    )

    assert isinstance(result, AIAnalysis)
    assert result.summary == VALID_AI_RESPONSE_PAYLOAD["summary"]
    assert len(result.strengths) == 2
    assert len(result.concerns) == 1
    assert result.concerns[0].severity == "medium"
    assert result.concerns[0].evidence != ""
    assert len(result.recommendations) == 1
    assert result.recommendations[0].priority == "high"
    assert "Starlette" in result.technical_overview.architecture or "modular" in result.technical_overview.architecture.lower()


async def test_ai_api_key_ausente_devuelve_none(fake_ai_client, monkeypatch):
    """Si no hay AI_API_KEY configurada, analyze_with_ai devuelve None sin peticiones HTTP."""
    called = False

    def handler(request: httpx.Request):
        nonlocal called
        called = True
        return httpx.Response(200, json={})

    fake_ai_client(handler)
    monkeypatch.setattr(settings, "ai_api_key", None)

    (
        repo,
        languages,
        contributors,
        commits,
        issues,
        pull_requests,
        releases,
        latest_release,
        activity,
        quality,
        metrics,
    ) = create_sample_repository_data()

    result = await analyze_with_ai(
        repo,
        languages,
        contributors,
        commits,
        issues,
        pull_requests,
        releases,
        latest_release,
        activity,
        quality,
        metrics,
    )

    assert result is None
    assert called is False


async def test_ai_timeout_lanza_ai_provider_error(fake_ai_client):
    """Un timeout de red lanza AIProviderError en run_ai_analysis y devuelve None en analyze_with_ai."""
    def handler(request: httpx.Request):
        raise httpx.ConnectTimeout("Timeout", request=request)

    fake_ai_client(handler)

    data = create_sample_repository_data()

    with pytest.raises(ai_exceptions.AIProviderError):
        await run_ai_analysis(*data, api_key="sk-test")

    # analyze_with_ai atrapa el error de forma segura
    safe_result = await analyze_with_ai(*data)
    assert safe_result is None


async def test_ai_rate_limit_429_lanza_rate_limit_error(fake_ai_client):
    """Un 429 lanza AIRateLimitError en run_ai_analysis."""
    fake_ai_client(lambda r: httpx.Response(429, json={"error": {"message": "Rate limit"}}))

    data = create_sample_repository_data()

    with pytest.raises(ai_exceptions.AIRateLimitError):
        await run_ai_analysis(*data, api_key="sk-test")


async def test_ai_auth_error_401_403_lanza_config_error(fake_ai_client):
    """Un 401 o 403 lanza AIConfigurationError."""
    fake_ai_client(lambda r: httpx.Response(401, json={"error": {"message": "Invalid API key"}}))

    data = create_sample_repository_data()

    with pytest.raises(ai_exceptions.AIConfigurationError):
        await run_ai_analysis(*data, api_key="sk-test")


async def test_ai_server_error_500_lanza_provider_error(fake_ai_client):
    """Un 500 del proveedor lanza AIProviderError."""
    fake_ai_client(lambda r: httpx.Response(500, json={"error": {"message": "Internal error"}}))

    data = create_sample_repository_data()

    with pytest.raises(ai_exceptions.AIProviderError):
        await run_ai_analysis(*data, api_key="sk-test")


async def test_ai_json_invalido_lanza_validation_error(fake_ai_client):
    """Si el modelo devuelve texto no JSON, se lanza AIResponseValidationError."""
    fake_ai_client(
        lambda r: httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"content": "Esto no es un JSON valido en absoluto"}}
                ]
            },
        )
    )

    data = create_sample_repository_data()

    with pytest.raises(ai_exceptions.AIResponseValidationError):
        await run_ai_analysis(*data, api_key="sk-test")


async def test_ai_schema_invalido_lanza_validation_error(fake_ai_client):
    """Si el JSON no cumple los campos obligatorios de AIAnalysis, lanza AIResponseValidationError."""
    fake_ai_client(
        lambda r: httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"content": json.dumps({"campo_inventado": 123})}}
                ]
            },
        )
    )

    data = create_sample_repository_data()

    with pytest.raises(ai_exceptions.AIResponseValidationError):
        await run_ai_analysis(*data, api_key="sk-test")


# --------------------------------------------------------------------------
# Tests de Integracion con el Endpoint /analyze
# --------------------------------------------------------------------------


def test_analyze_endpoint_con_ai_deshabilitada(client, fake_github):
    """GET /analyze/{owner}/{repo} funciona con ai_analysis=null cuando no hay API key."""
    fake_github(successful_handler)

    response = client.get("/analyze/encode/httpx")

    assert response.status_code == 200
    body = response.json()
    assert body["ai_analysis"] is None
    assert body["repository"]["name"] == "httpx"
    assert body["quality"]["tree_available"] is True
    assert body["metrics"]["total_files"] >= 0


def test_analyze_endpoint_con_ai_configurada_y_exitosa(
    client, fake_github, fake_ai_client, monkeypatch
):
    """GET /analyze/{owner}/{repo} incluye ai_analysis cuando AI esta configurada."""
    monkeypatch.setattr(settings, "ai_api_key", "sk-valid-key")

    def compound_handler(request: httpx.Request) -> httpx.Response:
        if "/chat/completions" in request.url.path:
            return ai_success_handler(request)
        return successful_handler(request)

    fake_github(compound_handler)
    fake_ai_client(compound_handler)

    response = client.get("/analyze/encode/httpx")

    assert response.status_code == 200
    body = response.json()
    assert body["ai_analysis"] is not None
    assert body["ai_analysis"]["summary"] == VALID_AI_RESPONSE_PAYLOAD["summary"]
    assert len(body["ai_analysis"]["concerns"]) == 1
    assert body["ai_analysis"]["concerns"][0]["severity"] == "medium"
