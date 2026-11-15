from flask import Blueprint, render_template

main = Blueprint("main", __name__)


@main.route("/")
def index():
    """Render the homepage."""
    return render_template("index.html")


@main.route("/projects/")
def projects():
    """Render the projects page."""
    return render_template("projects.html")


@main.route("/about/")
def about():
    """Render the about page."""
    return render_template("about.html")


@main.route("/contact/")
def contact():
    """Render the contact page."""
    return render_template("contact.html")
