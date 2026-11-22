"""Application factory for the Flask portfolio website."""


def create_app():
    """Create and configure the Flask application."""
    from flask import Flask

    from app.routes import main

    app = Flask(__name__)

    # Register the existing homepage routes until the multipage refactor begins.
    app.register_blueprint(main)

    return app
