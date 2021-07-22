from flask import Blueprint, render_template
import json

mod_home = Blueprint('home', __name__, url_prefix='/')


@mod_home.route("/")
def home():
    with open(f"program/sinf1ba-an1.json") as file:
        data = json.load(file)

        return render_template("home/index.html", title="Home", data=data)



