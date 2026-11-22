"""Helpers for resolving localized content and language fallback behavior."""

from typing import Any

SUPPORTED_LANGUAGES = ("en", "pt-br")
DEFAULT_LANGUAGE = "en"


def normalize_language(language: str | None) -> str:
    """Normalize common language identifiers to the site's supported codes."""
    if not language:
        return DEFAULT_LANGUAGE
    normalized = language.strip().lower().replace("_", "-")
    if normalized in SUPPORTED_LANGUAGES:
        return normalized
    if normalized.startswith("pt"):
        return "pt-br"
    return DEFAULT_LANGUAGE


def localized_value(value: Any, language: str, fallback_language: str = DEFAULT_LANGUAGE) -> Any:
    """Return the requested translation, falling back to the configured language."""
    if not isinstance(value, dict):
        return value
    selected_language = normalize_language(language)
    fallback = normalize_language(fallback_language)
    return value.get(selected_language, value.get(fallback))


def find_translation_url(urls: dict[str, str], language: str) -> str | None:
    """Return a URL for the requested language, if one was provided."""
    return urls.get(normalize_language(language))
