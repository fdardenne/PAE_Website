from flask import Blueprint, render_template

mod_home = Blueprint('home', __name__, url_prefix='/')


@mod_home.route("/")
def home():
    return render_template("home/index.html", title="Home")
