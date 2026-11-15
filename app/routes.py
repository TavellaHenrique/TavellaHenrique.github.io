from flask import Blueprint, render_template

from app.content import CONTENT

main = Blueprint("main", __name__)


@main.route("/")
def index():
    """Render the English homepage."""
    return render_template("index.html", content=CONTENT["en"])


@main.route("/pt-br/")
def index_pt_br():
    """Render the Brazilian Portuguese homepage."""
    return render_template("index.html", content=CONTENT["pt-br"])