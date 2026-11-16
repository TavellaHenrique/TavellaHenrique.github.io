
from pathlib import Path

from flask_frozen import Freezer

from app import create_app

app = create_app()

# Resolve the project root directory.
PROJECT_ROOT = Path(__file__).resolve().parent

# Configure the static website output directory.
app.config["FREEZER_DESTINATION"] = str(PROJECT_ROOT / "docs")
app.config["FREEZER_RELATIVE_URLS"] = True

# Initialize the static site generator.
freezer = Freezer(app)


if __name__ == "__main__":
    # Generate the static website.
    freezer.freeze()
