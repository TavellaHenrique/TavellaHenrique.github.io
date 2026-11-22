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


@pytest.mark.parametrize(
    ("route", "expected_title", "expected_message"),
    [
        ("/projects/", "Projects", "This page is currently under development."),
        ("/blog/", "Blog", "This page is currently under development."),
        ("/about/", "About", "This page is currently under development."),
        ("/pt-br/projetos/", "Projetos", "Esta página está em desenvolvimento."),
        ("/pt-br/blog/", "Blog", "Esta página está em desenvolvimento."),
        ("/pt-br/sobre/", "Sobre", "Esta página está em desenvolvimento."),
    ],
)
def test_placeholder_pages_display_localized_content(
    client, route, expected_title, expected_message
):
    """Verify placeholder pages display the correct localized content."""
    response = client.get(route)
    html = response.get_data(as_text=True)

    assert expected_title in html
    assert expected_message in html


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
