"""Load structured site content and Markdown bodies from the content directory."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ContentLoader:
    """Read JSON metadata and Markdown content from a configurable root directory."""

    def __init__(self, content_root: Path | str = "content") -> None:
        self.content_root = Path(content_root).resolve()

    def load_json(self, file_path: Path | str) -> dict[str, Any]:
        """Load a JSON file and ensure the root value is an object."""
        path = self._resolve_path(file_path)
        with path.open(encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            raise ValueError(f"Expected a JSON object in '{path}'.")
        return data

    def load_profile(self, language: str) -> dict[str, Any]:
        """Load the localized profile JSON."""
        return self.load_json(Path("profile") / f"{language}.json")

    def load_site_settings(self) -> dict[str, Any]:
        """Load global site settings."""
        return self.load_json("site/settings.json")

    def load_site_text(self, language: str) -> dict[str, Any]:
        """Load localized site labels and text."""
        return self.load_json(Path("site") / f"{language}.json")

    def load_projects(self) -> list[dict[str, Any]]:
        """Load all project metadata files, sorted by configured order."""
        projects: list[dict[str, Any]] = []
        directory = self.content_root / "projects"
        if not directory.exists():
            return projects

        for metadata_path in sorted(directory.glob("*/project.json")):
            project = self.load_json(metadata_path)
            project["_content_directory"] = metadata_path.parent
            projects.append(project)

        return sorted(projects, key=lambda item: item.get("order", 0))

    def load_project_markdown(self, project: dict[str, Any], language: str) -> str:
        """Load the project body for a language, or an empty body if unavailable."""
        file_map = project.get("content_files", {})
        file_name = file_map.get(language)
        if not file_name:
            return ""
        project_directory = Path(project["_content_directory"])
        path = self._resolve_path(project_directory / file_name)
        return path.read_text(encoding="utf-8")

    def load_posts(self, include_drafts: bool = True) -> list[dict[str, Any]]:
        """Load blog post metadata files; publication filtering is handled by services."""
        posts: list[dict[str, Any]] = []
        directory = self.content_root / "posts"
        if not directory.exists():
            return posts

        for metadata_path in sorted(directory.glob("*/post.json")):
            post = self.load_json(metadata_path)
            post["_content_directory"] = metadata_path.parent
            if include_drafts or post.get("status") != "draft":
                posts.append(post)
        return posts

    def load_post_markdown(self, post: dict[str, Any], language: str) -> str:
        """Load a localized blog post body, returning an empty body if missing."""
        file_map = post.get("content_files", {})
        file_name = file_map.get(language)
        if not file_name:
            return ""
        post_directory = Path(post["_content_directory"])
        path = self._resolve_path(post_directory / file_name)
        return path.read_text(encoding="utf-8")

    def _resolve_path(self, path: Path | str) -> Path:
        """Resolve a content path and prevent access outside the content root."""
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = self.content_root / candidate
        resolved = candidate.resolve()
        if resolved != self.content_root and self.content_root not in resolved.parents:
            raise ValueError(f"Content path escapes content root: '{path}'.")
        if not resolved.is_file():
            raise FileNotFoundError(f"Content file not found: '{resolved}'.")
        return resolved
