from flask import Flask

from app.routes import main


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Register the main application routes.
    app.register_blueprint(main)

    return app
