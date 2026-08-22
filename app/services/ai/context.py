"""Constructor del contexto estructurado y acotado para el modelo de IA.

Esta capa es una funcion pura: filtra, limita y resume los datos recopilados
por AI-Code-Analyzer sin realizar llamadas de red, sin descargar archivos y sin
incluir ningun token, clave de API ni secreto.
"""

from typing import Any

from app.schemas.repository import (
    Activity,
    Commit,
    Contributor,
    Issue,
    Metrics,
    PullRequest,
    Quality,
    Release,
    ReleaseDetail,
    Repository,
)

MAX_CONTEXT_CONTRIBUTORS = 5
MAX_CONTEXT_COMMITS = 5
MAX_CONTEXT_ISSUES = 5
MAX_CONTEXT_PULL_REQUESTS = 5
MAX_CONTEXT_EXTENSIONS = 5
MAX_CONTEXT_LARGEST_FILES = 5


def build_ai_context(
    repository: Repository,
    languages: dict[str, int],
    contributors: list[Contributor],
    recent_commits: list[Commit],
    issues: list[Issue],
    pull_requests: list[PullRequest],
    releases: list[ReleaseDetail],
    latest_release: Release | None,
    activity: Activity,
    quality: Quality,
    metrics: Metrics,
) -> dict[str, Any]:
    """Construye un payload de contexto compacto y fundamentado en evidencia."""
    # Top contributors acotado
    top_contributors = [
        {"username": c.username, "contributions": c.contributions}
        for c in contributors[:MAX_CONTEXT_CONTRIBUTORS]
    ]

    # Commits recientes acotados
    sampled_commits = [
        {
            "sha": c.sha,
            "message": c.message,
            "author": c.author,
            "date": c.date.isoformat(),
        }
        for c in recent_commits[:MAX_CONTEXT_COMMITS]
    ]

    # Issues acotados
    sampled_issues = [
        {
            "number": i.number,
            "title": i.title,
            "state": i.state,
            "created_at": i.created_at.isoformat(),
        }
        for i in issues[:MAX_CONTEXT_ISSUES]
    ]

    # Pull requests acotados
    sampled_prs = [
        {
            "number": pr.number,
            "title": pr.title,
            "state": pr.state,
            "is_merged": pr.merged_at is not None,
            "created_at": pr.created_at.isoformat(),
        }
        for pr in pull_requests[:MAX_CONTEXT_PULL_REQUESTS]
    ]

    # Top extensiones de archivo
    top_extensions = dict(
        list(metrics.file_extensions.items())[:MAX_CONTEXT_EXTENSIONS]
    )

    # Top archivos mas pesados
    top_largest_files = [
        {"path": f.path, "size_bytes": f.size_bytes}
        for f in metrics.largest_files[:MAX_CONTEXT_LARGEST_FILES]
    ]

    return {
        "repository": {
            "name": repository.name,
            "full_name": repository.full_name,
            "description": repository.description,
            "primary_language": repository.primary_language,
            "stars": repository.stars,
            "forks": repository.forks,
            "open_issues_count": repository.open_issues,
            "license": repository.license,
            "topics": repository.topics,
            "size_kb": repository.size_kb,
            "is_archived": repository.is_archived,
            "default_branch": repository.default_branch,
        },
        "languages": languages,
        "contributors": {
            "total_top_listed": len(contributors),
            "sampled_top": top_contributors,
        },
        "recent_commits": {
            "total_sampled": len(recent_commits),
            "sampled": sampled_commits,
        },
        "issues": {
            "total_sampled": len(issues),
            "open_count": sum(1 for i in issues if i.state == "open"),
            "closed_count": sum(1 for i in issues if i.state == "closed"),
            "sampled": sampled_issues,
        },
        "pull_requests": {
            "total_sampled": len(pull_requests),
            "open_count": sum(1 for pr in pull_requests if pr.state == "open"),
            "closed_count": sum(1 for pr in pull_requests if pr.state == "closed"),
            "merged_count": sum(1 for pr in pull_requests if pr.merged_at is not None),
            "sampled": sampled_prs,
        },
        "releases": {
            "total_sampled": len(releases),
            "published_count": sum(1 for r in releases if not r.draft),
            "draft_count": sum(1 for r in releases if r.draft),
            "prerelease_count": sum(1 for r in releases if r.prerelease),
            "latest_release": (
                {
                    "tag": latest_release.tag,
                    "name": latest_release.name,
                    "published_at": latest_release.published_at.isoformat(),
                }
                if latest_release
                else None
            ),
        },
        "activity": {
            "days_analyzed": activity.days,
            "total_commits_in_period": activity.total_commits,
            "total_issues_in_period": activity.total_issues,
            "total_prs_in_period": activity.total_pull_requests,
            "total_releases_in_period": activity.total_releases,
        },
        "quality": {
            "tree_available": quality.tree_available,
            "tree_truncated": quality.tree_truncated,
            "files_scanned": quality.files_scanned,
            "tests": {
                "detected": quality.tests.detected,
                "files_count": quality.tests.files,
                "directories": quality.tests.directories,
            },
            "documentation": {
                "readme": quality.documentation.readme,
                "contributing": quality.documentation.contributing,
                "docs_directory": quality.documentation.docs_directory,
                "files": quality.documentation.files,
            },
            "ci": {"detected": quality.ci.detected, "files": quality.ci.files},
            "linting": {"detected": quality.linting.detected, "files": quality.linting.files},
            "formatting": {
                "detected": quality.formatting.detected,
                "files": quality.formatting.files,
            },
            "type_checking": {
                "detected": quality.type_checking.detected,
                "files": quality.type_checking.files,
            },
            "dependencies": {
                "detected": quality.dependencies.detected,
                "files": quality.dependencies.files,
            },
            "coverage": {
                "configured": quality.coverage.configured,
                "percentage": quality.coverage.percentage,
                "files": quality.coverage.files,
            },
            "undetermined_config": quality.undetermined_config,
        },
        "metrics": {
            "tree_available": metrics.tree_available,
            "tree_truncated": metrics.tree_truncated,
            "total_files": metrics.total_files,
            "total_directories": metrics.total_directories,
            "source_files": metrics.source_files,
            "test_files": metrics.test_files,
            "documentation_files": metrics.documentation_files,
            "configuration_files": metrics.configuration_files,
            "top_file_extensions": top_extensions,
            "top_largest_files": top_largest_files,
            "lines_of_code": metrics.lines_of_code,
        },
    }
