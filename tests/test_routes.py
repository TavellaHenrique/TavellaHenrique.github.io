"""Tests for localized website routes."""

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
