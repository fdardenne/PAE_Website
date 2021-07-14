from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_admin import Admin, AdminIndexView


app = Flask(__name__)

# Configuration from config.py
app.config.from_object('config')

# SQLAlchemy
db = SQLAlchemy(app)

# To hash password
bcrypt = Bcrypt(app)

# Flask Login
login_manager = LoginManager(app)
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"


# Flask-Admin
class MyIndexAdminView(AdminIndexView):

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        else:
            flash("You don't have the right to access this page.", "danger")
            return redirect(url_for("home.home"))

f_admin = Admin(app, name='FlaskCMS', template_mode='bootstrap3', index_view=MyIndexAdminView())


# To handle 404 pages
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


from app.home.controllers import mod_home as home
from app.auth.controllers import mod_auth as auth

app.register_blueprint(home)
app.register_blueprint(auth)

db.create_all()
