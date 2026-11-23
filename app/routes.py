"""Localized routes for the portfolio website."""

from pathlib import Path

from flask import Blueprint, abort, render_template, url_for

from app.content import CONTENT
from app.services.content_loader import ContentLoader
from app.services.markdown_renderer import MarkdownRenderer

main = Blueprint("main", __name__)

# Resolve the content directory relative to the application source.
CONTENT_ROOT = Path(__file__).resolve().parents[1] / "content"
content_loader = ContentLoader(CONTENT_ROOT)
markdown_renderer = MarkdownRenderer()

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

    # Build the template context and allow page-specific overrides.
    context = {
        "content": localized_content,
        "site_text": site_text,
        "current_page": page,
        "page_title": site_text["navigation"][page],
        "alternate_url": url_for(alternate_endpoint),
        "language_urls": language_urls,
        "LANGUAGE_ROUTES": LANGUAGE_ROUTES,
    }

    context.update(extra_context or {})

    return render_template(template, **context)


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


def find_project_by_slug(slug: str, language: str) -> dict | None:
    """Find a project using its localized slug."""
    language_key = "pt-br" if language == "pt-br" else "en"

    for project in content_loader.load_projects():
        localized_slug = project.get("slug", {}).get(language_key)

        if localized_slug == slug:
            return project

    return None


def get_project_details(project: dict, language: str) -> dict:
    """Prepare localized project details and rendered Markdown."""
    language_key = "pt-br" if language == "pt-br" else "en"

    # Convert static file paths into paths relative to Flask's static directory.
    cover_image = project.get("cover_image")
    if cover_image and cover_image.startswith("app/static/"):
        cover_image = cover_image.removeprefix("app/static/")

    markdown_content = content_loader.load_project_markdown(
        project,
        language_key,
    )

    # Collect published posts related to this project.
    related_post_ids = set(project.get("related_post_ids", []))
    related_posts = []

    for post_data in content_loader.load_posts(include_drafts=False):
        post_id = post_data.get("id")

        # Support relationships defined from either side.
        if post_id not in related_post_ids and post_data.get("related_project_id") != project.get(
            "id"
        ):
            continue

        post_slug = post_data.get("slug", {}).get(language_key)
        post_title = post_data.get("title", {}).get(language_key)

        # Only include posts available in the requested language.
        if (
            language_key not in post_data.get("content_files", {})
            or not post_slug
            or not post_title
        ):
            continue

        post_endpoint = "main.post_detail" if language_key == "en" else "main.post_detail_pt_br"

        related_posts.append(
            {
                "id": post_id,
                "title": post_title,
                "url": url_for(post_endpoint, slug=post_slug),
                "published_at": post_data.get("published_at"),
            }
        )

    # Sort related posts from newest to oldest.
    related_posts.sort(
        key=lambda post: post.get("published_at") or "",
        reverse=True,
    )

    return {
        "id": project["id"],
        "slug": project.get("slug", {}).get(language_key),
        "title": project.get("title", {}).get(language_key),
        "description": project.get("short_description", {}).get(language_key),
        "status": project.get("status", "unknown"),
        "technologies": project.get("technologies", []),
        "tags": project.get("tags", []),
        "cover_image": cover_image,
        "cover_alt": project.get("cover_alt", {}).get(language_key, ""),
        "cover_caption": project.get("cover_caption", {}).get(language_key),
        "links": project.get("links", {}),
        "content_html": markdown_renderer.render(markdown_content),
        "related_posts": related_posts,
    }


def get_localized_posts(language: str) -> list[dict]:
    """Return published posts with metadata localized for the requested language."""
    language_key = "pt-br" if language == "pt-br" else "en"
    posts = content_loader.load_posts(include_drafts=False)
    localized_posts = []

    for post in posts:
        content_files = post.get("content_files", {})

        # Only include posts with content available in the requested language.
        if language_key not in content_files:
            continue

        slug = post.get("slug", {}).get(language_key)
        title = post.get("title", {}).get(language_key)

        # A localized URL and title are required for listing a post.
        if not slug or not title:
            continue

        cover_image = post.get("cover_image")

        # Convert repository paths into paths relative to Flask's static folder.
        if cover_image and cover_image.startswith("app/static/"):
            cover_image = cover_image.removeprefix("app/static/")

        localized_posts.append(
            {
                "id": post["id"],
                "slug": slug,
                "title": title,
                "description": post.get("description", {}).get(language_key, ""),
                "published_at": post.get("published_at"),
                "updated_at": post.get("updated_at"),
                "tags": post.get("tags", []),
                "cover_image": cover_image,
                "featured": post.get("featured", False),
                "related_project_id": post.get("related_project_id"),
            }
        )

    # Sort published posts by date, newest first.
    localized_posts.sort(
        key=lambda post: post.get("published_at") or "",
        reverse=True,
    )

    return localized_posts


def find_post_by_slug(slug: str, language: str) -> dict | None:
    """Find a published post by its localized slug."""
    language_key = "pt-br" if language == "pt-br" else "en"

    for post in content_loader.load_posts(include_drafts=False):
        localized_slug = post.get("slug", {}).get(language_key)

        if localized_slug == slug:
            return post

    return None


def get_post_details(post: dict, language: str) -> dict:
    """Prepare localized post metadata and rendered Markdown content."""
    language_key = "pt-br" if language == "pt-br" else "en"
    cover_image = post.get("cover_image")

    # Convert repository paths into paths relative to Flask's static folder.
    if cover_image and cover_image.startswith("app/static/"):
        cover_image = cover_image.removeprefix("app/static/")

    markdown_content = content_loader.load_post_markdown(
        post,
        language_key,
    )

    related_project = None
    related_project_id = post.get("related_project_id")

    if related_project_id:
        for project_data in content_loader.load_projects():
            if project_data.get("id") != related_project_id:
                continue

            project_slug = project_data.get("slug", {}).get(language_key)
            project_title = project_data.get("title", {}).get(language_key)

            if project_slug and project_title:
                project_endpoint = (
                    "main.project_detail" if language_key == "en" else "main.project_detail_pt_br"
                )

                related_project = {
                    "title": project_title,
                    "url": url_for(project_endpoint, slug=project_slug),
                }

            break

    return {
        "id": post["id"],
        "slug": post.get("slug", {}).get(language_key),
        "title": post.get("title", {}).get(language_key),
        "description": post.get("description", {}).get(language_key, ""),
        "published_at": post.get("published_at"),
        "updated_at": post.get("updated_at"),
        "tags": post.get("tags", []),
        "cover_image": cover_image,
        "featured": post.get("featured", False),
        "related_project_id": post.get("related_project_id"),
        "content_html": markdown_renderer.render(markdown_content),
        "related_project": related_project,
    }


def get_posts_by_tag(tag: str, language: str) -> list[dict]:
    """Return localized published posts associated with a tag."""
    posts = get_localized_posts(language)

    return [post for post in posts if tag in post.get("tags", [])]


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


@main.route("/pt-br/projetos/")
def projects_pt_br():
    """Render the Brazilian Portuguese projects listing."""
    return render_page(
        "pt-br",
        "projects",
        "projects/list.html",
        extra_context={"projects": get_localized_projects("pt-br")},
    )


@main.route("/projects/<slug>/")
def project_detail(slug: str):
    """Render an English project detail page."""
    project_data = find_project_by_slug(slug, "en")

    if project_data is None:
        abort(404)

    project = get_project_details(project_data, "en")

    # Link to the translated detail page when available.
    portuguese_slug = project_data.get("slug", {}).get("pt-br")
    language_urls = {
        "en": url_for("main.project_detail", slug=slug),
        "pt-br": (
            url_for("main.project_detail_pt_br", slug=portuguese_slug)
            if portuguese_slug
            else url_for("main.projects_pt_br")
        ),
    }

    return render_page(
        "en",
        "projects",
        "projects/detail.html",
        extra_context={
            "project": project,
            "language_urls": language_urls,
        },
    )


@main.route("/pt-br/projetos/<slug>/")
def project_detail_pt_br(slug: str):
    """Render a Brazilian Portuguese project detail page."""
    project_data = find_project_by_slug(slug, "pt-br")

    if project_data is None:
        abort(404)

    project = get_project_details(project_data, "pt-br")

    # Link to the translated detail page when available.
    english_slug = project_data.get("slug", {}).get("en")
    language_urls = {
        "en": (
            url_for("main.project_detail", slug=english_slug)
            if english_slug
            else url_for("main.projects")
        ),
        "pt-br": url_for("main.project_detail_pt_br", slug=slug),
    }

    return render_page(
        "pt-br",
        "projects",
        "projects/detail.html",
        extra_context={
            "project": project,
            "language_urls": language_urls,
        },
    )


@main.route("/blog/")
def blog():
    """Display the English blog listing."""
    return render_page(
        "en",
        "blog",
        "blog/list.html",
        extra_context={"posts": get_localized_posts("en")},
    )


@main.route("/pt-br/blog/")
def blog_pt_br():
    """Display the Portuguese blog listing."""
    return render_page(
        "pt-br",
        "blog",
        "blog/list.html",
        extra_context={"posts": get_localized_posts("pt-br")},
    )


@main.route("/blog/tags/<tag>/")
def blog_tag(tag: str):
    """Display English posts filtered by tag."""
    posts = get_posts_by_tag(tag, "en")

    if not posts:
        abort(404)

    language_urls = {
        "en": (url_for("main.blog_tag", tag=tag) if posts else url_for("main.blog")),
        "pt-br": url_for("main.blog_tag_pt_br", tag=tag),
    }

    return render_page(
        "en",
        "blog",
        "blog/tag.html",
        extra_context={"tag": tag, "posts": posts, "language_urls": language_urls},
    )


@main.route("/pt-br/blog/tags/<tag>/")
def blog_tag_pt_br(tag: str):
    """Display Portuguese posts filtered by tag."""
    posts = get_posts_by_tag(tag, "pt-br")

    if not posts:
        abort(404)

    language_urls = {
        "en": url_for("main.blog_tag", tag=tag),
        "pt-br": (url_for("main.blog_tag_pt_br", tag=tag) if posts else url_for("main.blog_pt_br")),
    }

    return render_page(
        "pt-br",
        "blog",
        "blog/tag.html",
        extra_context={"tag": tag, "posts": posts, "language_urls": language_urls},
    )


@main.route("/blog/<slug>/")
def post_detail(slug: str):
    """Display an English blog post."""
    post_data = find_post_by_slug(slug, "en")

    if post_data is None:
        abort(404)

    post = get_post_details(post_data, "en")
    portuguese_slug = post_data.get("slug", {}).get("pt-br")

    language_urls = {
        "en": url_for("main.post_detail", slug=slug),
        "pt-br": (
            url_for("main.post_detail_pt_br", slug=portuguese_slug)
            if portuguese_slug
            else url_for("main.blog_pt_br")
        ),
    }

    return render_page(
        "en",
        "blog",
        "blog/detail.html",
        extra_context={
            "post": post,
            "language_urls": language_urls,
        },
    )


@main.route("/pt-br/blog/<slug>/")
def post_detail_pt_br(slug: str):
    """Display a Portuguese blog post."""
    post_data = find_post_by_slug(slug, "pt-br")

    if post_data is None:
        abort(404)

    post = get_post_details(post_data, "pt-br")
    english_slug = post_data.get("slug", {}).get("en")

    language_urls = {
        "en": (
            url_for("main.post_detail", slug=english_slug) if english_slug else url_for("main.blog")
        ),
        "pt-br": url_for("main.post_detail_pt_br", slug=slug),
    }

    return render_page(
        "pt-br",
        "blog",
        "blog/detail.html",
        extra_context={
            "post": post,
            "language_urls": language_urls,
        },
    )


@main.route("/about/")
def about():
    """Render the English about page placeholder."""
    return render_page("en", "about")


@main.route("/pt-br/sobre/")
def about_pt_br():
    """Render the Brazilian Portuguese about page placeholder."""
    return render_page("pt-br", "about")
