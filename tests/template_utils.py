"""Utilities for handling template placeholder values in distribution tests."""
from __future__ import annotations

import os
from typing import Any, Iterable

import pytest

_PLACEHOLDER_STRINGS: tuple[str, ...] = (
    "OWNER/REPO",
    "OWNER.redoubt",
    "OWNER/tap",
    "com.OWNER.",
    "REPLACE_WITH_SHA256_FROM_RELEASE",
    "REPLACE_WITH_ACTUAL_SHA256",
    "REPLACE_WITH_",
    "YOUR NAME",
    "YOUR_ORG",
    "example.com/owner",
    "example.com/repo",
    "demo-secure-cli",
)


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


_ENFORCE_REAL_DISTRIBUTIONS = _env_flag("ENFORCE_REAL_DISTRIBUTIONS") or _env_flag("FAIL_ON_PLACEHOLDERS")


def contains_placeholder(value: Any) -> bool:
    """Return True if the provided value contains template placeholders."""
    if value is None:
        return False

    if isinstance(value, str):
        candidate = value.upper()
        return any(token.upper() in candidate for token in _PLACEHOLDER_STRINGS)

    if isinstance(value, dict):
        return any(contains_placeholder(v) for v in value.values())

    if isinstance(value, (list, tuple, set)):
        return any(contains_placeholder(v) for v in value)

    return False


def guard_placeholders(value: Any, description: str) -> None:
    """Skip or fail tests when template placeholders are encountered."""
    if not contains_placeholder(value):
        return

    message = (
        f"{description} still contains template placeholders. "
        "Configure staging or test distribution values to exercise this check."
    )
    if _ENFORCE_REAL_DISTRIBUTIONS:
        pytest.fail(message)
    pytest.skip(message)


def any_placeholders(iterable: Iterable[Any]) -> bool:
    """Helper to determine if any item in an iterable includes placeholders."""
    return any(contains_placeholder(item) for item in iterable)
