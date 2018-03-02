from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc as sql_alchemy_exceptions
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


def get_user(username):
    return Account.query.filter_by(username=username).first()


def get_user_by_id(userid):
    return Account.query.filter_by(id=userid).first()


def create_user(fname, lname, organization, email, uname, password):
    new_account = Account()
    new_account.first_name = fname
    new_account.last_name = lname
    new_account.organization = organization
    new_account.email = email
    new_account.username = uname
    new_account.password = generate_password_hash(password, method='sha256')
    try:
        db.session.add(new_account)
        db.session.commit()
    except sql_alchemy_exceptions.IntegrityError:
        db.session.rollback()
        email_exists = Account.query.filter_by(email=email).first()
        username_exists = Account.query.filter_by(username=uname).first()
        if email_exists:
            raise Exception(
                'A user has already been registered using this email.')
        elif username_exists:
            raise Exception(
                'A user has already been registered using this username.')


def edit_user(userid, fname, lname, organization, email, uname, password):
    user = get_user(Account.query.filter_by(id=userid).first().username)
    if fname != '':
        user.first_name = fname
    if lname != '':
        user.last_name = lname
    if organization != '':
        user.organization = organization
    if email != '':
        user.email = email
    if uname != '':
        user.username = uname
    if password != '':
        user.password = generate_password_hash(password, method='sha256')
    try:
        db.session.commit()
    except sql_alchemy_exceptions.IntegrityError:
        db.session.rollback()
        raise Exception('Something went wrong')


def validate_login_credentials(uname, password):
    user = get_user(uname)
    if user and check_password_hash(user.password, password):
        return True
    return False


