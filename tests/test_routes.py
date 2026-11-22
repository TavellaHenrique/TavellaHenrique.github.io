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


def test_homepage_routes_preserve_existing_content(client):
    """Verify the existing localized homepages continue to render."""
    english_response = client.get("/")
    portuguese_response = client.get("/pt-br/")

    assert english_response.status_code == 200
    assert portuguese_response.status_code == 200

    assert b"Pong By Allevat" in english_response.data
    assert b"Pong By Allevat" in portuguese_response.data


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


def test_projects_page_displays_project_metadata(client):
    """Verify the project listing renders metadata from project files."""
    response = client.get("/projects/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Pong By Allevat" in html
    assert "A reproduction of the classic Pong game" in html
    assert "Python 3.12" in html
    assert "Pygame" in html
    assert "Completed" in html
    assert "Featured" in html


def test_projects_page_displays_portuguese_metadata(client):
    """Verify the Portuguese listing uses localized project content."""
    response = client.get("/pt-br/projetos/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Pong By Allevat" in html
    assert "Uma reprodução do clássico Pong" in html
    assert "Concluído" in html
    assert "Destaque" in html


def test_projects_page_renders_project_cover(client):
    """Verify the project cover uses a valid static URL."""
    response = client.get("/projects/")
    html = response.get_data(as_text=True)

    assert "/static/images/pong-by-allevat.svg" in html


def test_projects_page_does_not_render_empty_github_link(client):
    """Verify links with missing metadata are not rendered."""
    response = client.get("/projects/")
    html = response.get_data(as_text=True)

    assert "Source code" not in html


def test_english_project_detail_page(client):
    """Verify the English project detail page renders its metadata and body."""
    response = client.get("/projects/pong-by-allevat/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Pong By Allevat" in html
    assert "Python 3.12" in html
    assert "Pygame" in html

    # Verify Markdown headings and lists are rendered as HTML.
    assert "<h2>Project objective</h2>" in html
    assert "<h2>Implemented features</h2>" in html
    assert "<li>Selectable visual themes</li>" in html


def test_portuguese_project_detail_page(client):
    """Verify the Portuguese project detail page renders localized content."""
    response = client.get("/pt-br/projetos/pong-by-allevat/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Pong By Allevat" in html
    assert "<h2>Objetivo do projeto</h2>" in html
    assert "<h2>Funcionalidades implementadas</h2>" in html
    assert "<li>Temas visuais selecionáveis</li>" in html


def test_project_detail_language_switcher_preserves_project(client):
    """Verify language switching links to the equivalent project page."""
    english_response = client.get("/projects/pong-by-allevat/")
    portuguese_response = client.get("/pt-br/projetos/pong-by-allevat/")

    english_html = english_response.get_data(as_text=True)
    portuguese_html = portuguese_response.get_data(as_text=True)

    assert 'href="/pt-br/projetos/pong-by-allevat/"' in english_html
    assert 'href="/projects/pong-by-allevat/"' in portuguese_html


def test_project_listing_links_to_details(client):
    """Verify project cards link to their detail pages."""
    english_response = client.get("/projects/")
    portuguese_response = client.get("/pt-br/projetos/")

    assert 'href="/projects/pong-by-allevat/"' in (english_response.get_data(as_text=True))
    assert 'href="/pt-br/projetos/pong-by-allevat/"' in (portuguese_response.get_data(as_text=True))


@pytest.mark.parametrize(
    "route",
    [
        "/projects/nonexistent-project/",
        "/pt-br/projetos/projeto-inexistente/",
    ],
)
def test_unknown_project_slug_returns_404(client, route):
    """Verify invalid project slugs return a not-found response."""
    response = client.get(route)

    assert response.status_code == 404
