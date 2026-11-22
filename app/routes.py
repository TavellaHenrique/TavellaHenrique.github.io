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


def render_page(language: str, page: str, template: str = "pages/placeholder.html"):
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
    )


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
    """Render the English projects page placeholder."""
    return render_page("en", "projects")


@main.route("/pt-br/projetos/")
def projects_pt_br():
    """Render the Brazilian Portuguese projects page placeholder."""
    return render_page("pt-br", "projects")


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
