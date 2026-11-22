"""Build the static website with Frozen-Flask."""

from pathlib import Path

from flask_frozen import Freezer

from app import create_app
from app.services.content_validator import ContentValidationError, ContentValidator

app = create_app()

# Resolve the project root directory.
PROJECT_ROOT = Path(__file__).resolve().parent

# Configure the static website output directory.
app.config["FREEZER_DESTINATION"] = str(PROJECT_ROOT / "docs")
app.config["FREEZER_RELATIVE_URLS"] = True

# Initialize the static site generator.
freezer = Freezer(app)


if __name__ == "__main__":
    # Validate content before generating public pages.
    validation_errors = ContentValidator(PROJECT_ROOT / "content").validate_all()
    if validation_errors:
        raise ContentValidationError(validation_errors)

    # Generate the static website only when content is valid.
    freezer.freeze()
