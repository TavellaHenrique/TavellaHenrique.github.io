"""Validate content structure and basic cross-file integrity."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any


SUPPORTED_LANGUAGES = {"en", "pt-br"}
PROJECT_STATUSES = {"in_progress", "completed", "archived"}
POST_STATUSES = {"draft", "published"}
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ContentValidationError(ValueError):
    """Raised when one or more content validation checks fail."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("Content validation failed:\n- " + "\n- ".join(errors))


class ContentValidator:
    """Validate content files against the initial content model."""

    def __init__(self, content_root: Path | str = "content") -> None:
        self.content_root = Path(content_root).resolve()

    def validate_all(self) -> list[str]:
        """Return all validation errors found in profile, site, projects, and posts."""
        errors: list[str] = []
        errors.extend(self.validate_profiles())
        errors.extend(self.validate_site_settings())
        errors.extend(self.validate_projects())
        errors.extend(self.validate_posts())
        errors.extend(self.validate_relationships())
        return errors

    def validate_profiles(self) -> list[str]:
        """Check profile JSON files for required fields and valid value types."""
        errors: list[str] = []
        for language in SUPPORTED_LANGUAGES:
            path = self.content_root / "profile" / f"{language}.json"
            data = self._read_json(path, errors)
            if data is None:
                continue
            for field in ("name", "presentation", "skills", "education", "links"):
                if field not in data:
                    errors.append(f"{path}: missing required field '{field}'.")
            if not isinstance(data.get("skills", []), list):
                errors.append(f"{path}: 'skills' must be a list.")
            if not isinstance(data.get("links", []), list):
                errors.append(f"{path}: 'links' must be a list.")
        return errors

    def validate_site_settings(self) -> list[str]:
        """Validate global site settings and localized site text files."""
        errors: list[str] = []
        settings_path = self.content_root / "site" / "settings.json"
        settings = self._read_json(settings_path, errors)
        if settings is not None:
            languages = settings.get("supported_languages")
            if not isinstance(languages, list) or not languages:
                errors.append(f"{settings_path}: 'supported_languages' must be a non-empty list.")
            elif not set(languages).issubset(SUPPORTED_LANGUAGES):
                errors.append(f"{settings_path}: contains unsupported language codes.")
            if settings.get("default_language") not in SUPPORTED_LANGUAGES:
                errors.append(f"{settings_path}: unsupported 'default_language'.")

        for language in SUPPORTED_LANGUAGES:
            path = self.content_root / "site" / f"{language}.json"
            localized = self._read_json(path, errors)
            if localized is not None:
                for field in ("title", "description", "navigation", "footer"):
                    if field not in localized:
                        errors.append(f"{path}: missing required field '{field}'.")
        return errors

    def validate_projects(self) -> list[str]:
        """Validate project metadata, localized fields, and Markdown files."""
        errors: list[str] = []
        directory = self.content_root / "projects"
        if not directory.exists():
            return errors
        seen_ids: set[str] = set()
        seen_slugs: dict[str, set[str]] = {language: set() for language in SUPPORTED_LANGUAGES}
        for path in sorted(directory.glob("*/project.json")):
            project = self._read_json(path, errors)
            if project is None:
                continue
            project_id = project.get("id")
            if not isinstance(project_id, str) or not project_id:
                errors.append(f"{path}: 'id' must be a non-empty string.")
            elif project_id in seen_ids:
                errors.append(f"{path}: duplicate project id '{project_id}'.")
            seen_ids.add(project_id)
            self._validate_slug_map(project.get("slug"), path, errors)
            for language, slug in (project.get("slug") or {}).items():
                if language in seen_slugs and isinstance(slug, str):
                    if slug in seen_slugs[language]:
                        errors.append(f"{path}: duplicate project slug '{slug}' for '{language}'.")
                    seen_slugs[language].add(slug)
            for field in ("title", "short_description"):
                value = project.get(field)
                if not isinstance(value, dict) or not any(
                    language in value and isinstance(value[language], str) and value[language]
                    for language in SUPPORTED_LANGUAGES
                ):
                    errors.append(f"{path}: '{field}' must provide at least one localized value.")
            if project.get("status") not in PROJECT_STATUSES:
                errors.append(f"{path}: invalid project status.")
            if not isinstance(project.get("technologies", []), list):
                errors.append(f"{path}: 'technologies' must be a list.")
            if not isinstance(project.get("tags", []), list):
                errors.append(f"{path}: 'tags' must be a list.")
            elif not all(isinstance(tag, str) and tag for tag in project.get("tags", [])):
                errors.append(f"{path}: tags must contain non-empty strings.")
            self._validate_date(project.get("start_date"), path, "start_date", errors)
            self._validate_date(project.get("completion_date"), path, "completion_date", errors)
            self._validate_date_order(project.get("start_date"), project.get("completion_date"), path, errors)
            self._validate_content_files(project.get("content_files"), path.parent, path, errors)
            self._validate_local_media(project.get("cover_image"), path, errors)
            if project.get("cover_image"):
                cover_alt = project.get("cover_alt")
                if not isinstance(cover_alt, dict) or not any(
                    language in cover_alt and isinstance(cover_alt[language], str) and cover_alt[language]
                    for language in SUPPORTED_LANGUAGES
                ):
                    errors.append(f"{path}: a cover image requires at least one localized alt text.")
            media_items = project.get("media", [])
            if not isinstance(media_items, list):
                errors.append(f"{path}: 'media' must be a list.")
                media_items = []
            for media in media_items:
                if isinstance(media, str):
                    self._validate_local_media(media, path, errors)
                elif isinstance(media, dict):
                    self._validate_local_media(media.get("path"), path, errors)
                else:
                    errors.append(f"{path}: media entries must be paths or objects.")
        return errors

    def validate_posts(self) -> list[str]:
        """Validate blog post metadata and body files, including drafts."""
        errors: list[str] = []
        directory = self.content_root / "posts"
        if not directory.exists():
            return errors
        seen_ids: set[str] = set()
        seen_slugs: dict[str, set[str]] = {language: set() for language in SUPPORTED_LANGUAGES}
        for path in sorted(directory.glob("*/post.json")):
            post = self._read_json(path, errors)
            if post is None:
                continue
            post_id = post.get("id")
            if not isinstance(post_id, str) or not post_id:
                errors.append(f"{path}: 'id' must be a non-empty string.")
            elif post_id in seen_ids:
                errors.append(f"{path}: duplicate post id '{post_id}'.")
            seen_ids.add(post_id)
            self._validate_slug_map(post.get("slug"), path, errors)
            for language, slug in (post.get("slug") or {}).items():
                if language in seen_slugs and isinstance(slug, str):
                    if slug in seen_slugs[language]:
                        errors.append(f"{path}: duplicate post slug '{slug}' for '{language}'.")
                    seen_slugs[language].add(slug)
            for field in ("title", "description"):
                value = post.get(field)
                if not isinstance(value, dict) or not any(
                    language in value and isinstance(value[language], str) and value[language]
                    for language in SUPPORTED_LANGUAGES
                ):
                    errors.append(f"{path}: '{field}' must provide at least one localized value.")
            if post.get("status") not in POST_STATUSES:
                errors.append(f"{path}: invalid post status.")
            if post.get("language") not in SUPPORTED_LANGUAGES:
                errors.append(f"{path}: invalid post language.")
            if not isinstance(post.get("tags", []), list) or not all(
                isinstance(tag, str) and tag for tag in post.get("tags", [])
            ):
                errors.append(f"{path}: 'tags' must be a list of non-empty strings.")
            self._validate_date(post.get("published_at"), path, "published_at", errors)
            self._validate_date(post.get("updated_at"), path, "updated_at", errors)
            self._validate_content_files(post.get("content_files"), path.parent, path, errors)
            self._validate_local_media(post.get("cover_image"), path, errors)
            if post.get("status") == "published" and not post.get("published_at"):
                errors.append(f"{path}: published posts require 'published_at'.")
            self._validate_date_order(post.get("published_at"), post.get("updated_at"), path, errors)
            if post.get("status") == "published" and post.get("language") not in (
                post.get("content_files") or {}
            ):
                errors.append(f"{path}: published post must have a Markdown file for its primary language.")
        return errors

    def _read_json(self, path: Path, errors: list[str]) -> dict[str, Any] | None:
        """Read a JSON object, recording errors instead of aborting validation."""
        if not path.is_file():
            errors.append(f"{path}: file is missing.")
            return None
        try:
            import json

            with path.open(encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict):
                errors.append(f"{path}: JSON root must be an object.")
                return None
            return data
        except (OSError, ValueError) as error:
            errors.append(f"{path}: cannot read JSON ({error}).")
            return None

    def _validate_slug_map(self, value: Any, path: Path, errors: list[str]) -> None:
        """Ensure localized slug mappings are valid and present."""
        if not isinstance(value, dict) or not value:
            errors.append(f"{path}: 'slug' must be a non-empty object keyed by language.")
            return
        for language, slug in value.items():
            if language not in SUPPORTED_LANGUAGES:
                errors.append(f"{path}: unsupported slug language '{language}'.")
            if not isinstance(slug, str) or not SLUG_PATTERN.fullmatch(slug):
                errors.append(f"{path}: invalid slug for '{language}'.")

    def _validate_content_files(
        self, file_map: Any, content_directory: Path, metadata_path: Path, errors: list[str]
    ) -> None:
        """Check localized Markdown references and ensure files exist within their folder."""
        if not isinstance(file_map, dict):
            errors.append(f"{metadata_path}: 'content_files' must be an object.")
            return
        if not file_map:
            errors.append(f"{metadata_path}: at least one localized Markdown file is required.")
        for language, file_name in file_map.items():
            if language not in SUPPORTED_LANGUAGES:
                errors.append(f"{metadata_path}: unsupported content language '{language}'.")
            if not isinstance(file_name, str) or not file_name:
                errors.append(f"{metadata_path}: invalid content file for '{language}'.")
                continue
            candidate = (content_directory / file_name).resolve()
            if content_directory.resolve() not in candidate.parents:
                errors.append(f"{metadata_path}: content file path escapes its directory.")
            elif not candidate.is_file():
                errors.append(f"{metadata_path}: content file '{file_name}' is missing.")

    def _validate_local_media(self, media_path: Any, metadata_path: Path, errors: list[str]) -> None:
        """Validate media paths as local files within the project repository."""
        if media_path is None:
            return
        if not isinstance(media_path, str) or not media_path:
            errors.append(f"{metadata_path}: media path must be a non-empty string or null.")
            return
        if media_path.startswith(("http://", "https://")):
            errors.append(f"{metadata_path}: external media URLs are not allowed: '{media_path}'.")
            return
        candidate = (self.content_root.parent / media_path).resolve()
        repository_root = self.content_root.parent.resolve()
        if repository_root not in candidate.parents and candidate != repository_root:
            errors.append(f"{metadata_path}: media path escapes repository root.")
        elif not candidate.is_file():
            errors.append(f"{metadata_path}: media file '{media_path}' is missing.")

    def _validate_date(
        self, value: Any, path: Path, field: str, errors: list[str], required: bool = False
    ) -> None:
        """Validate ISO date values."""
        if value is None and not required:
            return
        if not isinstance(value, str):
            errors.append(f"{path}: '{field}' must be an ISO date string or null.")
            return
        try:
            date.fromisoformat(value)
        except ValueError:
            errors.append(f"{path}: '{field}' is not a valid ISO date.")

    def _validate_date_order(
        self, start_date: Any, completion_date: Any, path: Path, errors: list[str]
    ) -> None:
        """Ensure completion date is not earlier than the start date."""
        if not start_date or not completion_date:
            return
        try:
            if date.fromisoformat(completion_date) < date.fromisoformat(start_date):
                errors.append(f"{path}: completion_date cannot precede start_date.")
        except (TypeError, ValueError):
            # Date-format errors are reported by the dedicated date checks.
            return

    def validate_relationships(self) -> list[str]:
        """Validate project/post relationship IDs against existing content."""
        errors: list[str] = []
        project_ids = {
            project.get("id")
            for project in self._load_metadata("projects", "project.json", errors)
        }
        post_ids = {
            post.get("id")
            for post in self._load_metadata("posts", "post.json", errors)
        }

        settings_path = self.content_root / "site" / "settings.json"
        settings = self._read_json(settings_path, errors)
        if settings:
            featured_ids = settings.get("home", {}).get("featured_project_ids", [])
            if not isinstance(featured_ids, list):
                errors.append(f"{settings_path}: 'featured_project_ids' must be a list.")
            else:
                for project_id in featured_ids:
                    if project_id not in project_ids:
                        errors.append(f"{settings_path}: featured project '{project_id}' does not exist.")

        for path in sorted((self.content_root / "projects").glob("*/project.json")):
            project = self._read_json(path, errors)
            if not project:
                continue
            for post_id in project.get("related_post_ids", []):
                if post_id not in post_ids:
                    errors.append(f"{path}: related post '{post_id}' does not exist.")

        for path in sorted((self.content_root / "posts").glob("*/post.json")):
            post = self._read_json(path, errors)
            if not post:
                continue
            related_project = post.get("related_project_id")
            if related_project and related_project not in project_ids:
                errors.append(f"{path}: related project '{related_project}' does not exist.")
        return errors

    def _load_metadata(self, directory_name: str, file_name: str, errors: list[str]) -> list[dict[str, Any]]:
        """Read metadata records for relationship checks."""
        records: list[dict[str, Any]] = []
        directory = self.content_root / directory_name
        if not directory.exists():
            return records
        for path in sorted(directory.glob(f"*/{file_name}")):
            data = self._read_json(path, errors)
            if data is not None:
                records.append(data)
        return records
