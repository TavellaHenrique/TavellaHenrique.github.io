"""Tests for language normalization and localized value lookup."""

from app.services.localization import find_translation_url, localized_value, normalize_language


def test_language_normalization_accepts_common_variants() -> None:
    assert normalize_language("PT_BR") == "pt-br"
    assert normalize_language("pt") == "pt-br"
    assert normalize_language("EN-us") == "en"
    assert normalize_language(None) == "en"


def test_localized_value_uses_fallback_when_translation_is_missing() -> None:
    value = {"en": "English text"}

    assert localized_value(value, "pt-br") == "English text"


def test_translation_url_lookup_returns_none_when_missing() -> None:
    urls = {"en": "/blog/example/"}

    assert find_translation_url(urls, "pt-br") is None
