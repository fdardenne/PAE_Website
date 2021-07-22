from app import db, login_manager
from flask_login import UserMixin
from flask_admin.contrib.sqla import ModelView

# Flask login 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean(), default=False)
    inscription_year = db.Column(db.Integer(), nullable=False)
    minor = db.Column(db.String(100), default="")

    def __repr__(self):
        return f"User: ('{self.username}')', '{self.email}'"


