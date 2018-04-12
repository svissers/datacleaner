from app import database as db
from .models import User
from app.Project.models import Project, Access
from werkzeug.security import generate_password_hash, check_password_hash
from app.Project.operations import delete_project_with_id


def create_user(first_name, last_name, email, username, password):
    """
    Creates a user with provided information
    :param first_name: first name for user
    :param last_name: last name for user
    :param email: email for user
    :param username: username for user
    :param password: password for user
    :exception RuntimeError: a user already exists with given username/email
    """
    # Search for possible existing user with given username or email
    email_used = User.query.filter_by(email=email).first()
    username_used = User.query.filter_by(username=username).first()
    # Throw RuntimeError if the provided username or email is already in use
    # Create a new user otherwise
    if email_used:
        raise RuntimeError(
            'A user has already been registered using this email.')
    elif username_used:
        raise RuntimeError(
            'A user has already been registered using this username.')
    else:
        new_user = User(first_name, last_name, email, username, password)
        db.session.add(new_user)
        db.session.commit()


def get_user_with_id(user_id):
    """
    :param user_id: id used for lookup
    :return User: user instance associated with id
    """
    return User.query.filter_by(id=user_id).first()


def get_user_with_username(username):
    """
    :param username: username used for lookup
    :return User: User instance associated with given username
    """
    return User.query.filter_by(username=username).first()


def delete_user_with_id(user_id):
    """
    Deletes User instance associated with given id
    :param user_id: id used for lookup
    :exception RuntimeError: no user associated with id
    """
    user = get_user_with_id(user_id)
    if user is None:
        raise RuntimeError('No user associated with this id.')
    else:
        for project in user.projects:
            delete_project_with_id(project.id, user_id)
        db.session.delete(user)
        db.session.commit()


def delete_user_with_username(username):
    """
    Deletes User instance associated with given username
    :param username: username used for lookup
    :exception RuntimeError: no user associated with username
    """
    user = get_user_with_username(username)
    if user is None:
        raise RuntimeError('No user associated with this username.')
    else:
        for project in user.projects:
            delete_project_with_id(project.id, user.id)
        db.session.delete(user)
        db.session.commit()


def update_user_with_id(
        user_id,
        first_name=None,
        last_name=None,
        email=None,
        username=None,
        password=None
):
    """
    Updates user information associated with given id
    :param user_id: id used for lookup
    :param first_name: new first name (optional)
    :param last_name: new last name (optional)
    :param email: new email name (optional)
    :param username: new username (optional)
    :param password: new password (optional)
    :exception RuntimeError: no user associated with id
    :exception RuntimeError: email/username already in use
    """
    # Search for possible existing user with given username or email
    email_used = User.query. \
        filter(User.email == email). \
        filter(User.id != user_id). \
        first()
    username_used = User.query. \
        filter(User.username == username). \
        filter(User.id != user_id). \
        first()
    user = get_user_with_id(user_id)
    # Throw RuntimeError if the provided username or email is already in use
    # Update user info otherwise
    if email_used:
        raise RuntimeError(
            'A user has already been registered using this email.')
    elif username_used:
        raise RuntimeError(
            'A user has already been registered using this username.')
    elif user is None:
        raise RuntimeError('No user associated with this id.')
    else:
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if email:
            user.email = email
        if username:
            if user.username == 'admin' and username != 'admin':
                raise RuntimeError(
                    "Username of admin can't be changed")
            user.username = username
        if password:
            user.password = generate_password_hash(password, method='sha256')
        db.session.commit()


def update_admin_status(user_id, admin):
    """
    Updates admin status for user associated with given id
    :param user_id: id used for lookup
    :param admin: new admin status
    :exception RuntimeError: no user associated with id
    """
    user = get_user_with_id(user_id)
    if user is None:
        raise RuntimeError('No user associated with this id.')
    else:
        user.admin = admin
        db.session.commit()


def update_disabled_status(user_id, disabled):
    """
    Updates disabled status for user associated with given id
    :param user_id: id used for lookup
    :param disabled: new disabled status
    :exception RuntimeError: no user associated with id
    """
    user = get_user_with_id(user_id)
    if user is None:
        raise RuntimeError('No user associated with this id.')
    else:
        user.disabled = disabled
        db.session.commit()


def validate_login_credentials(candidate_username, candidate_password):
    """
    Validates provided user credentials
    :param candidate_username: username candidate for validation
    :param candidate_password: password candidate for validation
    :return (bool, string): bool indicating validity, string additional info
    """
    user_info = get_user_with_username(candidate_username)
    if user_info and check_password_hash(
            user_info.password,
            candidate_password
    ):
        if user_info.disabled:
            return False, 'User disabled, contact system administrator.'
        return True, 'Valid Credentials'
    return False, 'Incorrect username or password, please try again.'


def init_admin():
    """
    Initializes admin account if it doesn't exist
    """
    username_exists = User.query.filter_by(username='admin').first()
    if not username_exists:
        create_user('', '', 'admin@datacleaner.com', 'admin', 'admin')
    User.query.filter_by(username='admin').first().admin = True
    db.session.commit()
