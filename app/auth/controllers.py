from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from app import bcrypt, db
from app.auth.forms import RegistrationForm, LoginForm
from app.auth.models import User
import app.auth.admin

mod_auth = Blueprint("auth", __name__)


@mod_auth.route("/auth/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.home"))

    form = LoginForm()

    # If the form has been submitted
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # If the username and the password match
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            flash("Successfully logged in", "primary")
            login_user(user, remember=form.remember.data)
            nextpage = request.args.get("next")
            return redirect(nextpage) if nextpage else redirect(url_for("home.home"))
        else:
            # The flash function add the alert message in the frontend
            flash("Bad login", "danger")

    return render_template("auth/login.html", title="Login", form=form)


@mod_auth.route("/auth/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home.home"))
    form = RegistrationForm()

    if form.validate_on_submit():

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Account created", "primary")

        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", title="Register", form=form)


@mod_auth.route("/auth/logout")
def logout():
    if current_user.is_authenticated:
        return redirect(url_for("home.home"))
    logout_user()
    return redirect(url_for("home.home"))