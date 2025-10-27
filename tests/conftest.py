"""Pytest configuration hooks for the redoubt-release-template test suite."""
import os


def _env_flag(name: str) -> bool:
    """Interpret common truthy strings from environment variables."""
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def pytest_addoption(parser):
    """Register CLI flags used by the published distribution tests."""
    parser.addoption(
        "--release-tag",
        action="store",
        default=os.getenv("RELEASE_TAG"),
        help="Specific release tag to test (e.g., v1.0.0). "
             "Can also be provided via RELEASE_TAG env var.",
    )
    parser.addoption(
        "--use-latest",
        action="store_true",
        default=_env_flag("PYTEST_PUBLISHED_USE_LATEST"),
        help="Test the latest published release (set PYTEST_PUBLISHED_USE_LATEST=1 to enable by default).",
    )
    parser.addoption(
        "--github-repo",
        action="store",
        default=os.getenv("GITHUB_REPO", "Borduas-Holdings/redoubt-release-template-"),
        help="GitHub repository in OWNER/REPO format (defaults to this project).",
    )
