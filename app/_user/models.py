from app import database as db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


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
    organization = db.Column(db.String(25))
    email = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(80))
    is_staff = db.Column(db.Boolean(False))
    is_admin = db.Column(db.Boolean(False))

    def __init__(self, fname, lname, organization, email, uname, password):
        """Initializes a user instance"""
        self.first_name = fname
        self.last_name = lname
        self.organization = organization
        self.email = email
        self.username = uname
        self.password = generate_password_hash(password, method='sha256')

    def add_to_database(self):
        """Adds user instance to database"""
        email_exists = self.query.filter_by(email=self.email).first()
        username_exists = self.query.filter_by(username=self.username).first()
        if not email_exists and not username_exists:
            db.session.add(self)
            db.session.commit()
        elif email_exists:
            raise Exception(
                'A user has already been registered using this email.')
        elif username_exists:
            raise Exception(
                'A user has already been registered using this username.')

    @classmethod
    def get_by_name(cls, username):
        """Returns user info associated with given username"""
        return User.query.filter_by(username=username).first()

    @classmethod
    def get_by_id(cls, user_id):
        """Returns user info associated with given id"""
        return User.query.filter_by(id=user_id).first()

    @classmethod
    def update_by_id(cls, id, fname, lname, organization, email, uname, pw):
        """Updates user info associated with given id"""
        user = User.get_by_id(id)
        if fname != '':
            print("ello")
            user.first_name = fname
        if lname:
            user.last_name = lname
        if organization:
            user.organization = organization
        if email:
            user.email = email
        if uname:
            user.username = uname
        if pw:
            user.password = generate_password_hash(pw, method='sha256')
        db.session.commit()

    @classmethod
    def validate_login_credentials(cls, uname_candidate, pw_candidate):
        """
        Validates candidate user credentials
        Returns:
        --> True if candidate credentials are valid
        --> False otherwise    
        """
        user_info = User.get_by_name(uname_candidate)
        if user_info and check_password_hash(user_info.password, pw_candidate):
            return True
        return False
