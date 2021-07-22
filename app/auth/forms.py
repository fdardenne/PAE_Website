from flask_wtf import FlaskForm
from .models import User
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from flask_login import current_user
from app import bcrypt
from datetime import date

class RegistrationForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])

    inscription_year = IntegerField("Année d'inscription en bac1 SINF", validators=[DataRequired(), NumberRange(min=2015,max=date.today().year)])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    confirm_password = PasswordField("Confirmation mot de passe", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("S'enregistrer")

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("Le nom d'utilisateur a déjà été enregistré")

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError("L'email a déjà été enregistré")
        


class LoginForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    remember = BooleanField("Enregistrer ma session")
    submit = SubmitField("Login")