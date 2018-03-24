from app import database as db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash


class User(db.Model, UserMixin):
    """Represents table holding user data in our database"""

    # Table name to be used in database
    # If not provided class name is used which is a problem when using
    # postgres because user is a reserved keyword
    __tablename__ = 'user_data'

    # Table columns
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(db.String(25))
    last_name = db.Column(db.String(25))
    email = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    admin = db.Column(db.Boolean(), default=0)
    disabled = db.Column(db.Boolean(), default=0)

    # User is parent of action, thus this relationship helper class
    actions = db.relationship('Action', backref='user', lazy='dynamic')

    def __init__(self, fname, lname, email, uname, password):
        """Initializes a user instance"""
        self.first_name = fname
        self.last_name = lname
        self.email = email
        self.username = uname
        self.password = generate_password_hash(password, method='sha256')
