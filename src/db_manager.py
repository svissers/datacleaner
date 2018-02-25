from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc as sql_alchemy_exceptions
from forms import SignUpForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash

# See following link on how to import and use this module:
# https://stackoverflow.com/questions/9692962/flask-sqlalchemy-import-context-issue/9695045#9695045
db = SQLAlchemy()


class Account(db.Model):
    """docstring for User"""
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(db.String(25))
    last_name = db.Column(db.String(25))
    organization = db.Column(db.String(25))
    email = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean(False))

    @staticmethod
    def create_user(form: SignUpForm):
        new_account = Account()
        new_account.first_name = form.first_name.data
        new_account.last_name = form.last_name.data
        new_account.organization = form.organization.data
        new_account.email = form.email.data
        new_account.username = form.username.data
        new_account.password = generate_password_hash(form.password.data,
                                                      method='sha256')
        try:
            db.session.add(new_account)
            db.session.commit()
        except sql_alchemy_exceptions.IntegrityError:
            db.session.rollback()
            email_exists = Account.query.filter_by(
                email=form.email.data).first()
            username_exists = Account.query.filter_by(
                username=form.username.data).first()
            if email_exists:
                raise Exception(
                    'A user has already been registered using this email.')
            elif username_exists:
                raise Exception(
                    'A user has already been registered using this username.')

    @staticmethod
    def validate_login_credentials(form: LoginForm):
        user = Account.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            return True
        return False
