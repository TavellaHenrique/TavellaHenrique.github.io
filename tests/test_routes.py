"""Tests for localized website routes."""

import re

import pytest

from app import create_app


@pytest.fixture
def client():
    """Create a Flask test client."""
    app = create_app()
    app.config["TESTING"] = True

    return app.test_client()


def make_project(
    project_id: str = "test-project",
    english_slug: str = "test-project",
    portuguese_slug: str = "projeto-teste",
) -> dict:
    """Create isolated project metadata for route tests."""
    return {
        "id": project_id,
        "slug": {
            "en": english_slug,
            "pt-br": portuguese_slug,
        },
        "title": {
            "en": "Test Project",
            "pt-br": "Projeto de Teste",
        },
        "short_description": {
            "en": "Test project description.",
            "pt-br": "Descrição do projeto de teste.",
        },
        "status": "completed",
        "featured": True,
        "technologies": ["Python", "Flask"],
        "tags": ["testing"],
        "start_date": None,
        "completion_date": None,
        "cover_image": None,
        "cover_alt": {"en": "", "pt-br": ""},
        "cover_caption": {"en": "", "pt-br": ""},
        "media": [],
        "links": {"github": None, "demo": None},
        "related_post_ids": [],
        "order": 1,
        "content_files": {"en": "en.md", "pt-br": "pt-br.md"},
    }


def make_post(
    post_id: str = "test-post",
    english_slug: str = "test-post",
    portuguese_slug: str = "artigo-teste",
    published_at: str = "2026-01-15",
    status: str = "published",
    content_files: dict | None = None,
) -> dict:
    """Create isolated post metadata for route tests."""
    return {
        "id": post_id,
        "slug": {
            "en": english_slug,
            "pt-br": portuguese_slug,
        },
        "title": {
            "en": "Test Article",
            "pt-br": "Artigo de Teste",
        },
        "description": {
            "en": "Test article description.",
            "pt-br": "Descrição do artigo de teste.",
        },
        "status": status,
        "language": "en",
        "published_at": published_at,
        "updated_at": None,
        "tags": ["testing"],
        "cover_image": None,
        "related_project_id": None,
        "featured": True,
        "content_files": content_files
        or {
            "en": "en.md",
            "pt-br": "pt-br.md",
        },
    }


@pytest.mark.parametrize(
    "route",
    [
        "/",
        "/pt-br/",
        "/projects/",
        "/pt-br/projetos/",
        "/blog/",
        "/pt-br/blog/",
        "/about/",
        "/pt-br/sobre/",
    ],
)
def test_localized_routes_return_success(client, route):
    """Verify all planned routes respond successfully."""
    response = client.get(route)

    assert response.status_code == 200


def test_localized_homepages_render(client):
    """Verify both localized homepages render successfully."""
    for route in ("/", "/pt-br/"):
        response = client.get(route)

        assert response.status_code == 200


@pytest.mark.parametrize(
    ("route", "active_page", "expected_href"),
    [
        ("/", "home", "/"),
        ("/projects/", "projects", "/projects/"),
        ("/blog/", "blog", "/blog/"),
        ("/about/", "about", "/about/"),
        ("/pt-br/", "home", "/pt-br/"),
        ("/pt-br/projetos/", "projects", "/pt-br/projetos/"),
        ("/pt-br/blog/", "blog", "/pt-br/blog/"),
        ("/pt-br/sobre/", "about", "/pt-br/sobre/"),
    ],
)
def test_navigation_marks_current_page(client, route, active_page, expected_href):
    """Verify the current page is marked in the global navigation."""
    response = client.get(route)
    html = response.get_data(as_text=True)

    assert response.status_code == 200

    # Match the active link regardless of HTML attribute ordering.
    active_link_pattern = (
        rf'<a\b(?=[^>]*href="{re.escape(expected_href)}")'
        rf'(?=[^>]*aria-current="page")[^>]*>'
    )

    assert re.search(active_link_pattern, html)


@pytest.mark.parametrize(
    ("route", "expected_pt_url", "expected_en_url"),
    [
        ("/", "/pt-br/", "/"),
        ("/projects/", "/pt-br/projetos/", "/projects/"),
        ("/blog/", "/pt-br/blog/", "/blog/"),
        ("/about/", "/pt-br/sobre/", "/about/"),
        ("/pt-br/", "/pt-br/", "/"),
        ("/pt-br/projetos/", "/pt-br/projetos/", "/projects/"),
        ("/pt-br/blog/", "/pt-br/blog/", "/blog/"),
        ("/pt-br/sobre/", "/pt-br/sobre/", "/about/"),
    ],
)
def test_language_switcher_links_to_equivalent_page(
    client, route, expected_pt_url, expected_en_url
):
    """Verify language links preserve the current page."""
    response = client.get(route)
    html = response.get_data(as_text=True)

    assert f'href="{expected_pt_url}"' in html
    assert f'href="{expected_en_url}"' in html


def test_projects_page_displays_project_metadata(client, monkeypatch):
    """Verify the project listing renders injected metadata."""
    from app.routes import content_loader

    project = make_project()

    monkeypatch.setattr(
        content_loader,
        "load_projects",
        lambda: [project],
    )

    response = client.get("/projects/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Test Project" in html
    assert "Test project description." in html
    assert "Python" in html
    assert "Flask" in html
    assert "Completed" in html
    assert "Featured" in html


def test_projects_page_displays_localized_metadata(client, monkeypatch):
    """Verify the Portuguese listing uses localized project metadata."""
    from app.routes import content_loader

    project = make_project()

    monkeypatch.setattr(
        content_loader,
        "load_projects",
        lambda: [project],
    )

    response = client.get("/pt-br/projetos/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Projeto de Teste" in html
    assert "Descrição do projeto de teste." in html
    assert "Concluído" in html
    assert "Destaque" in html


def test_projects_page_does_not_render_empty_github_link(client, monkeypatch):
    """Verify unavailable external links are not rendered."""
    from app.routes import content_loader

    project = make_project()

    monkeypatch.setattr(
        content_loader,
        "load_projects",
        lambda: [project],
    )

    response = client.get("/projects/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Source code" not in html


def test_projects_page_renders_local_cover(client, monkeypatch):
    """Verify project cover paths are converted to static URLs."""
    from app.routes import content_loader

    project = make_project()
    project["cover_image"] = "app/static/images/test/cover.webp"
    project["cover_alt"] = {
        "en": "Test cover",
        "pt-br": "Capa de teste",
    }

    monkeypatch.setattr(
        content_loader,
        "load_projects",
        lambda: [project],
    )

    response = client.get("/projects/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "/static/images/test/cover.webp" in html
    assert "Test cover" in html


def test_english_project_detail_page(client, monkeypatch):
    """Verify English project details render injected data and Markdown."""
    from app.routes import content_loader

    project = make_project()

    monkeypatch.setattr(
        content_loader,
        "load_projects",
        lambda: [project],
    )
    monkeypatch.setattr(
        content_loader,
        "load_project_markdown",
        lambda project, language: (
            "## Project objective\n\nTest objective.\n\n## Implemented features\n\n- Test feature\n"
        ),
    )

    response = client.get("/projects/test-project/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Test Project" in html
    assert "Python" in html
    assert "Flask" in html
    assert "<h2>Project objective</h2>" in html
    assert "<h2>Implemented features</h2>" in html
    assert "<li>Test feature</li>" in html


def test_portuguese_project_detail_page(client, monkeypatch):
    """Verify Portuguese project details render localized data."""
    from app.routes import content_loader

    project = make_project()

    monkeypatch.setattr(
        content_loader,
        "load_projects",
        lambda: [project],
    )
    monkeypatch.setattr(
        content_loader,
        "load_project_markdown",
        lambda project, language: (
            "## Objetivo do projeto\n\n"
            "Objetivo de teste.\n\n"
            "## Funcionalidades implementadas\n\n"
            "- Funcionalidade de teste\n"
        ),
    )

    response = client.get("/pt-br/projetos/projeto-teste/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Projeto de Teste" in html
    assert "<h2>Objetivo do projeto</h2>" in html
    assert "<h2>Funcionalidades implementadas</h2>" in html
    assert "<li>Funcionalidade de teste</li>" in html


def test_project_detail_language_switcher_preserves_project(client, monkeypatch):
    """Verify language switching preserves the injected project."""
    from app.routes import content_loader

    project = make_project()

    monkeypatch.setattr(
        content_loader,
        "load_projects",
        lambda: [project],
    )
    monkeypatch.setattr(
        content_loader,
        "load_project_markdown",
        lambda project, language: "Test content.",
    )

    english_response = client.get("/projects/test-project/")
    portuguese_response = client.get("/pt-br/projetos/projeto-teste/")

    english_html = english_response.get_data(as_text=True)
    portuguese_html = portuguese_response.get_data(as_text=True)

    assert 'href="/pt-br/projetos/projeto-teste/"' in english_html
    assert 'href="/projects/test-project/"' in portuguese_html


def test_project_listing_links_to_details(client, monkeypatch):
    """Verify injected project cards link to localized details."""
    from app.routes import content_loader

    project = make_project()

    monkeypatch.setattr(
        content_loader,
        "load_projects",
        lambda: [project],
    )

    english_response = client.get("/projects/")
    portuguese_response = client.get("/pt-br/projetos/")

    assert 'href="/projects/test-project/"' in english_response.get_data(as_text=True)
    assert 'href="/pt-br/projetos/projeto-teste/"' in portuguese_response.get_data(as_text=True)


@pytest.mark.parametrize(
    "route",
    [
        "/projects/nonexistent-project/",
        "/pt-br/projetos/projeto-inexistente/",
    ],
)
def test_unknown_project_slug_returns_404(client, monkeypatch, route):
    """Verify unknown project slugs return 404."""
    from app.routes import content_loader

    monkeypatch.setattr(
        content_loader,
        "load_projects",
        lambda: [],
    )

    response = client.get(route)

    assert response.status_code == 404


def test_english_blog_listing_is_empty(client, monkeypatch):
    """Verify the English empty state when no posts are provided."""
    from app.routes import content_loader

    monkeypatch.setattr(
        content_loader,
        "load_posts",
        lambda include_drafts=False: [],
    )

    response = client.get("/blog/")

    assert response.status_code == 200
    assert "No articles published yet." in response.get_data(as_text=True)


def test_portuguese_blog_listing_is_empty(client, monkeypatch):
    """Verify the Portuguese empty state when no posts are provided."""
    from app.routes import content_loader

    monkeypatch.setattr(
        content_loader,
        "load_posts",
        lambda include_drafts=False: [],
    )

    response = client.get("/pt-br/blog/")

    assert response.status_code == 200
    assert "Nenhum artigo publicado ainda." in response.get_data(as_text=True)


def test_english_blog_listing_displays_injected_post(client, monkeypatch):
    """Verify the English blog listing renders an injected post."""
    from app.routes import content_loader

    post = make_post()

    monkeypatch.setattr(
        content_loader,
        "load_posts",
        lambda include_drafts=False: [post],
    )

    response = client.get("/blog/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Test Article" in html
    assert "Test article description." in html
    assert "testing" in html
    assert "Read article" in html
    assert "/blog/test-post/" in html


def test_portuguese_blog_listing_displays_localized_post(client, monkeypatch):
    """Verify the Portuguese blog listing renders localized metadata."""
    from app.routes import content_loader

    post = make_post()

    monkeypatch.setattr(
        content_loader,
        "load_posts",
        lambda include_drafts=False: [post],
    )

    response = client.get("/pt-br/blog/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Artigo de Teste" in html
    assert "Descrição do artigo de teste." in html
    assert "Ler artigo" in html
    assert "/pt-br/blog/artigo-teste/" in html


def test_localized_posts_are_sorted_by_publication_date(monkeypatch):
    """Verify published posts are sorted newest first."""
    from app.routes import content_loader, get_localized_posts

    posts = [
        make_post(
            post_id="older-post",
            english_slug="older-post",
            portuguese_slug="artigo-antigo",
            published_at="2026-01-10",
        ),
        make_post(
            post_id="newer-post",
            english_slug="newer-post",
            portuguese_slug="artigo-recente",
            published_at="2026-02-10",
        ),
    ]

    monkeypatch.setattr(
        content_loader,
        "load_posts",
        lambda include_drafts=False: posts,
    )

    localized_posts = get_localized_posts("en")

    assert [post["id"] for post in localized_posts] == [
        "newer-post",
        "older-post",
    ]


def test_blog_listing_excludes_drafts(client, monkeypatch):
    """Verify draft posts are excluded from the blog listing."""
    from app.routes import content_loader

    published_post = make_post(post_id="published-post")
    draft_post = make_post(
        post_id="draft-post",
        english_slug="draft-post",
        portuguese_slug="rascunho",
        status="draft",
    )

    all_posts = [published_post, draft_post]

    monkeypatch.setattr(
        content_loader,
        "load_posts",
        lambda include_drafts=False: (
            all_posts
            if include_drafts
            else [post for post in all_posts if post["status"] == "published"]
        ),
    )

    response = client.get("/blog/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Test Article" in html
    assert "draft-post" not in html


def test_english_post_detail_page(client, monkeypatch):
    """Verify the English article page renders injected content."""
    from app.routes import content_loader

    post = make_post()

    monkeypatch.setattr(
        content_loader,
        "load_posts",
        lambda include_drafts=False: [post],
    )
    monkeypatch.setattr(
        content_loader,
        "load_post_markdown",
        lambda post, language: "## Test section\n\nTest article content.\n\n- Test item\n",
    )

    response = client.get("/blog/test-post/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Test Article" in html
    assert "Test article description." in html
    assert "Published" in html
    assert "<h2>Test section</h2>" in html
    assert "Test article content." in html
    assert "<li>Test item</li>" in html


def test_portuguese_post_detail_page(client, monkeypatch):
    """Verify the Portuguese article page renders localized content."""
    from app.routes import content_loader

    post = make_post()

    monkeypatch.setattr(
        content_loader,
        "load_posts",
        lambda include_drafts=False: [post],
    )
    monkeypatch.setattr(
        content_loader,
        "load_post_markdown",
        lambda post, language: (
            "## Seção de teste\n\nConteúdo do artigo de teste.\n\n- Item de teste\n"
        ),
    )

    response = client.get("/pt-br/blog/artigo-teste/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Artigo de Teste" in html
    assert "Descrição do artigo de teste." in html
    assert "Publicado em" in html
    assert "<h2>Seção de teste</h2>" in html
    assert "Conteúdo do artigo de teste." in html
    assert "<li>Item de teste</li>" in html


def test_post_language_switcher_preserves_article(client, monkeypatch):
    """Verify language switching preserves the injected article."""
    from app.routes import content_loader

    post = make_post()

    monkeypatch.setattr(
        content_loader,
        "load_posts",
        lambda include_drafts=False: [post],
    )
    monkeypatch.setattr(
        content_loader,
        "load_post_markdown",
        lambda post, language: "Test content.",
    )

    english_response = client.get("/blog/test-post/")
    portuguese_response = client.get("/pt-br/blog/artigo-teste/")

    english_html = english_response.get_data(as_text=True)
    portuguese_html = portuguese_response.get_data(as_text=True)

    assert 'href="/pt-br/blog/artigo-teste/"' in english_html
    assert 'href="/blog/test-post/"' in portuguese_html


@pytest.mark.parametrize(
    "route",
    [
        "/blog/nonexistent-post/",
        "/pt-br/blog/artigo-inexistente/",
    ],
)
def test_unknown_post_slug_returns_404(client, monkeypatch, route):
    """Verify unknown post slugs return 404."""
    from app.routes import content_loader

    monkeypatch.setattr(
        content_loader,
        "load_posts",
        lambda include_drafts=False: [],
    )

    response = client.get(route)

    assert response.status_code == 404


def test_draft_post_detail_returns_404(client, monkeypatch):
    """Verify draft posts cannot be accessed directly."""
    from app.routes import content_loader

    draft_post = make_post(
        status="draft",
        english_slug="draft-post",
        portuguese_slug="rascunho",
    )

    monkeypatch.setattr(
        content_loader,
        "load_posts",
        lambda include_drafts=False: [draft_post] if include_drafts else [],
    )

    response = client.get("/blog/draft-post/")

    assert response.status_code == 404


def test_english_tag_page_filters_posts(client, monkeypatch):
    """Verify tag pages display only matching posts."""
    from app.routes import content_loader

    tagged_post = make_post(post_id="tagged-post")
    unrelated_post = make_post(
        post_id="unrelated-post",
        english_slug="unrelated-post",
        portuguese_slug="post-sem-tag",
    )
    unrelated_post["tags"] = ["python"]

    monkeypatch.setattr(
        content_loader,
        "load_posts",
        lambda include_drafts=False: [tagged_post, unrelated_post],
    )

    response = client.get("/blog/tags/testing/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Test Article" in html
    assert "unrelated-post" not in html


def test_portuguese_tag_page_filters_posts(client, monkeypatch):
    """Verify the Portuguese tag page displays matching posts."""
    from app.routes import content_loader

    post = make_post()

    monkeypatch.setattr(
        content_loader,
        "load_posts",
        lambda include_drafts=False: [post],
    )

    response = client.get("/pt-br/blog/tags/testing/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Artigo de Teste" in html
    assert "Descrição do artigo de teste." in html


@pytest.mark.parametrize(
    "route",
    [
        "/blog/tags/nonexistent/",
        "/pt-br/blog/tags/inexistente/",
    ],
)
def test_unknown_tag_returns_404(client, monkeypatch, route):
    """Verify tags without published posts return 404."""
    from app.routes import content_loader

    monkeypatch.setattr(
        content_loader,
        "load_posts",
        lambda include_drafts=False: [],
    )

    response = client.get(route)

    assert response.status_code == 404


def test_blog_listing_tags_link_to_tag_pages(client, monkeypatch):
    """Verify post tags link to their localized tag pages."""
    from app.routes import content_loader

    post = make_post()

    monkeypatch.setattr(
        content_loader,
        "load_posts",
        lambda include_drafts=False: [post],
    )

    english_response = client.get("/blog/")
    portuguese_response = client.get("/pt-br/blog/")

    assert 'href="/blog/tags/testing/"' in english_response.get_data(as_text=True)
    assert 'href="/pt-br/blog/tags/testing/"' in portuguese_response.get_data(as_text=True)


def test_tag_language_switcher_preserves_tag(client, monkeypatch):
    """Verify tag language switching preserves the tag when available."""
    from app.routes import content_loader

    post = make_post()

    monkeypatch.setattr(
        content_loader,
        "load_posts",
        lambda include_drafts=False: [post],
    )

    english_response = client.get("/blog/tags/testing/")
    portuguese_response = client.get("/pt-br/blog/tags/testing/")

    assert 'href="/pt-br/blog/tags/testing/"' in english_response.get_data(as_text=True)
    assert 'href="/blog/tags/testing/"' in portuguese_response.get_data(as_text=True)


def test_tag_language_switcher_falls_back_to_blog(client, monkeypatch):
    """Verify language switching falls back when the tag has no translation."""
    from app.routes import content_loader

    post = make_post(
        content_files={"en": "en.md"},
    )

    monkeypatch.setattr(
        content_loader,
        "load_posts",
        lambda include_drafts=False: [post],
    )

    response = client.get("/blog/tags/testing/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'href="/blog/"' in html


def test_english_blog_search_controls_are_rendered(client, monkeypatch):
    """Verify English blog search controls and language notice."""
    from app.routes import content_loader

    monkeypatch.setattr(
        content_loader,
        "load_posts",
        lambda include_drafts=False: [make_post()],
    )

    response = client.get("/blog/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'id="blog-search"' in html
    assert 'id="blog-tag-filter"' in html
    assert 'id="blog-search-reset"' in html
    assert "Search is limited to articles in English." in html
    assert "Search by title, description or tag..." in html
    assert "Clear filters" in html


def test_portuguese_blog_search_controls_are_rendered(client, monkeypatch):
    """Verify Portuguese blog search controls and language notice."""
    from app.routes import content_loader

    monkeypatch.setattr(
        content_loader,
        "load_posts",
        lambda include_drafts=False: [make_post()],
    )

    response = client.get("/pt-br/blog/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'id="blog-search"' in html
    assert 'id="blog-tag-filter"' in html
    assert 'id="blog-search-reset"' in html
    assert "A busca está limitada aos artigos em português." in html
    assert "Buscar por título, descrição ou tag..." in html
    assert "Limpar filtros" in html


def test_blog_post_cards_include_search_index(client, monkeypatch):
    """Verify rendered post cards expose searchable metadata."""
    from app.routes import content_loader

    monkeypatch.setattr(
        content_loader,
        "load_posts",
        lambda include_drafts=False: [make_post()],
    )

    response = client.get("/blog/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "data-search-index=" in html
    assert "Test Article" in html
    assert "Test article description." in html


@pytest.mark.parametrize(
    ("route", "expected_previous", "expected_next"),
    [
        ("/blog/", "Previous page", "Next page"),
        ("/pt-br/blog/", "Página anterior", "Próxima página"),
    ],
)
def test_blog_pagination_controls_are_rendered(
    client,
    monkeypatch,
    route,
    expected_previous,
    expected_next,
):
    """Verify pagination controls are rendered in both languages."""
    from app.routes import content_loader

    monkeypatch.setattr(
        content_loader,
        "load_posts",
        lambda include_drafts=False: [make_post()],
    )

    response = client.get(route)
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'id="blog-pagination"' in html
    assert 'id="blog-pagination-previous"' in html
    assert 'id="blog-pagination-next"' in html
    assert expected_previous in html
    assert expected_next in html
