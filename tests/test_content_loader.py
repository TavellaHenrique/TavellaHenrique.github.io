"""Tests for loading content files from the content directory."""

from pathlib import Path

import pytest

from app.services.content_loader import ContentLoader

CONTENT_ROOT = Path(__file__).parents[1] / "content"


def test_load_profile_for_supported_language() -> None:
    loader = ContentLoader(CONTENT_ROOT)

    profile = loader.load_profile("pt-br")

    assert profile["name"] == "Henrique Tavella"
    assert profile["skills"]
    assert profile["links"]


def test_load_site_settings_and_localized_text() -> None:
    loader = ContentLoader(CONTENT_ROOT)

    settings = loader.load_site_settings()
    localized = loader.load_site_text("en")

    assert settings["default_language"] == "en"
    assert localized["navigation"]["blog"] == "Blog"


def test_load_project_metadata_and_markdown() -> None:
    loader = ContentLoader(CONTENT_ROOT)
    project = loader.load_projects()[0]

    body = loader.load_project_markdown(project, "pt-br")

    assert project["id"] == "pong-by-allevat"
    assert "Objetivo do projeto" in body


def test_loader_rejects_paths_outside_content_root(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    content_root.mkdir()
    outside_file = tmp_path / "private.json"
    outside_file.write_text("{}", encoding="utf-8")

    loader = ContentLoader(content_root)

    with pytest.raises(ValueError, match="escapes content root"):
        loader.load_json(outside_file)


def test_loader_excludes_drafts_when_public_posts_are_requested(tmp_path: Path) -> None:
    import json

    posts_directory = tmp_path / "posts"
    draft_directory = posts_directory / "draft-post"
    published_directory = posts_directory / "published-post"
    draft_directory.mkdir(parents=True)
    published_directory.mkdir(parents=True)

    # Create minimal metadata records to verify draft filtering behavior.
    (draft_directory / "post.json").write_text(
        json.dumps({"id": "draft-post", "status": "draft"}), encoding="utf-8"
    )
    (published_directory / "post.json").write_text(
        json.dumps({"id": "published-post", "status": "published"}), encoding="utf-8"
    )

    loader = ContentLoader(tmp_path)

    public_posts = loader.load_posts(include_drafts=False)
    all_posts = loader.load_posts(include_drafts=True)

    assert [post["id"] for post in public_posts] == ["published-post"]
    assert len(all_posts) == 2
