"""Tests for structural and integrity validation of content files."""

from pathlib import Path


from app.services.content_validator import ContentValidator


CONTENT_ROOT = Path(__file__).parents[1] / "content"


def test_existing_content_passes_validation() -> None:
    validator = ContentValidator(CONTENT_ROOT)

    assert validator.validate_all() == []


def test_invalid_slug_is_reported(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    (content_root / "projects" / "invalid-project").mkdir(parents=True)
    (content_root / "projects" / "invalid-project" / "project.json").write_text(
        '{"id":"invalid-project","slug":{"en":"Bad Slug","pt-br":"slug-invalido"}}',
        encoding="utf-8",
    )

    validator = ContentValidator(content_root)
    errors = validator.validate_projects()

    assert any("invalid slug" in error for error in errors)


def test_missing_markdown_file_is_reported(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    project_directory = content_root / "projects" / "missing-body"
    project_directory.mkdir(parents=True)
    metadata = {
        "id": "missing-body",
        "slug": {"en": "missing-body", "pt-br": "missing-body"},
        "title": {"en": "Missing Body", "pt-br": "Sem conteúdo"},
        "short_description": {"en": "Desc", "pt-br": "Desc"},
        "status": "completed",
        "content_files": {"en": "en.md", "pt-br": "pt-br.md"},
    }
    import json

    (project_directory / "project.json").write_text(json.dumps(metadata), encoding="utf-8")

    validator = ContentValidator(content_root)
    errors = validator.validate_projects()


    assert any("content file 'en.md' is missing" in error for error in errors)


def test_date_order_validation_reports_completion_before_start(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    project_directory = content_root / "projects" / "bad-dates"
    project_directory.mkdir(parents=True)
    metadata = {
        "id": "bad-dates",
        "slug": {"en": "bad-dates", "pt-br": "bad-dates"},
        "title": {"en": "Bad Dates", "pt-br": "Datas inválidas"},
        "short_description": {"en": "Desc", "pt-br": "Desc"},
        "status": "completed",
        "start_date": "2026-05-01",
        "completion_date": "2026-04-01",
        "content_files": {},
    }
    import json

    (project_directory / "project.json").write_text(json.dumps(metadata), encoding="utf-8")

    errors = ContentValidator(content_root).validate_projects()


    assert any("completion_date cannot precede start_date" in error for error in errors)
