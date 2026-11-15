from flask_frozen import Freezer

from app import create_app

app = create_app()

# Configure the static website output directory.
app.config["FREEZER_DESTINATION"] = "docs"
app.config["FREEZER_RELATIVE_URLS"] = True

# Initialize the static site generator.
freezer = Freezer(app)


if __name__ == "__main__":
    # Generate the static website.
    freezer.freeze()
