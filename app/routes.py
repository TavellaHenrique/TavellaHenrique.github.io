"""Localized routes for the portfolio website."""

from pathlib import Path

from flask import Blueprint, render_template, url_for

from app.content import CONTENT
from app.services.content_loader import ContentLoader

main = Blueprint("main", __name__)

# Resolve the content directory relative to the application source.
CONTENT_ROOT = Path(__file__).resolve().parents[1] / "content"
content_loader = ContentLoader(CONTENT_ROOT)

# Map each page to its equivalent route in the other language.
LANGUAGE_ROUTES = {
    "en": {
        "home": "main.index",
        "projects": "main.projects",
        "blog": "main.blog",
        "about": "main.about",
    },
    "pt-br": {
        "home": "main.index_pt_br",
        "projects": "main.projects_pt_br",
        "blog": "main.blog_pt_br",
        "about": "main.about_pt_br",
    },
}


def render_page(
    language: str,
    page: str,
    template: str = "pages/placeholder.html",
    extra_context: dict | None = None,
):
    """Render a page with its language, navigation and alternate-language URL."""
    localized_content = CONTENT["en" if language == "en" else "pt-br"]
    site_text = content_loader.load_site_text(language)

    alternate_language = "pt-br" if language == "en" else "en"
    alternate_endpoint = LANGUAGE_ROUTES[alternate_language][page]

    language_urls = {
        "en": url_for(LANGUAGE_ROUTES["en"][page]),
        "pt-br": url_for(LANGUAGE_ROUTES["pt-br"][page]),
    }

    return render_template(
        template,
        content=localized_content,
        site_text=site_text,
        current_page=page,
        page_title=site_text["navigation"][page],
        alternate_url=url_for(alternate_endpoint),
        language_urls=language_urls,
        LANGUAGE_ROUTES=LANGUAGE_ROUTES,
        **(extra_context or {}),
    )


def get_localized_projects(language: str) -> list[dict]:
    """Prepare project metadata for the localized listing page."""
    projects = content_loader.load_projects()
    localized_projects = []

    language_key = "pt-br" if language == "pt-br" else "en"

    for project in projects:
        title = project.get("title", {}).get(language_key)
        description = project.get("short_description", {}).get(language_key)

        # Skip projects without the required localized listing content.
        if not title or not description:
            continue

        cover_image = project.get("cover_image")
        if cover_image and cover_image.startswith("app/static/"):
            cover_image = cover_image.removeprefix("app/static/")

        localized_projects.append(
            {
                "id": project["id"],
                "slug": project.get("slug", {}).get(language_key),
                "title": title,
                "description": description,
                "status": project.get("status", "unknown"),
                "featured": project.get("featured", False),
                "technologies": project.get("technologies", []),
                "tags": project.get("tags", []),
                "cover_image": cover_image,
                "cover_alt": project.get("cover_alt", {}).get(language_key, title),
                "cover_caption": project.get("cover_caption", {}).get(language_key),
                "links": project.get("links", {}),
            }
        )

    return localized_projects


@main.route("/")
def index():
    """Render the English homepage."""
    return render_page("en", "home", "index.html")


@main.route("/pt-br/")
def index_pt_br():
    """Render the Brazilian Portuguese homepage."""
    return render_page("pt-br", "home", "index.html")


@main.route("/projects/")
def projects():
    """Render the English projects listing."""
    return render_page(
        "en",
        "projects",
        "projects/list.html",
        extra_context={"projects": get_localized_projects("en")},
    )


0


@main.route("/pt-br/projetos/")
def projects_pt_br():
    """Render the Brazilian Portuguese projects listing."""
    return render_page(
        "pt-br",
        "projects",
        "projects/list.html",
        extra_context={"projects": get_localized_projects("pt-br")},
    )


@main.route("/blog/")
def blog():
    """Render the English blog page placeholder."""
    return render_page("en", "blog")


@main.route("/pt-br/blog/")
def blog_pt_br():
    """Render the Brazilian Portuguese blog page placeholder."""
    return render_page("pt-br", "blog")


@main.route("/about/")
def about():
    """Render the English about page placeholder."""
    return render_page("en", "about")


@main.route("/pt-br/sobre/")
def about_pt_br():
    """Render the Brazilian Portuguese about page placeholder."""
    return render_page("pt-br", "about")
