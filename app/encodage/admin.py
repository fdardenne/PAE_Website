from app import f_admin, db
from flask_admin import BaseView, expose, AdminIndexView
from flask import redirect, url_for, request, flash
from flask_login import current_user
from app.encodage.models import SucceededCourse
from flask_admin.contrib.sqla import ModelView


class EncodageModelView(ModelView):

    column_searchable_list = ['username']

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        if not login.current_user.is_authenticated:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        else:
            flash("You don't have the right to access this page.", "danger")
            return redirect(url_for("home.home"))


f_admin.add_view(EncodageModelView(SucceededCourse, db.session))
