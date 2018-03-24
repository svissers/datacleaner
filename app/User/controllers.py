from app import login_manager as lm
from .forms import (
    SignUpForm,
    LoginForm,
    EditForm
)
from flask import (
    Blueprint,
    render_template,
    flash,
    redirect,
    url_for,
    jsonify,
    request
)
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)
from .operations import (
    get_user_with_id,
    get_user_with_username,
    create_user,
    validate_login_credentials,
    update_user_with_id
)
from .models import User

_user = Blueprint('user_bp', __name__, url_prefix='/user')
lm.login_view = 'user_bp.login'


@lm.user_loader
def load_user(user_id):
    return get_user_with_id(user_id)


@_user.route('/autocomplete', methods=['GET'])
def autocomplete():
    users = User.query.with_entities(User.username).all()
    return jsonify(users)


@_user.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        try:
            create_user(
                form.first_name.data,
                form.last_name.data,
                form.email.data,
                form.username.data,
                form.password.data
            )
            flash('You have been registered and can now log in.', 'success')
            return redirect(url_for('user_bp.login'))
        except RuntimeError as error:
            flash(str(error), 'danger')
    return render_template('_user/signup.html', form=form)


@_user.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # Upon submission of the form it gets validated,
    # if it's valid and de login info is valid we redirect to the dashboard
    if form.validate_on_submit():
        result = User.validate_login_credentials(form.username.data,
                                                 form.password.data)
        if result[0] is True:
            user = get_user_with_username(form.username.data)
            login_user(user)
            return redirect(url_for('main_bp.dashboard'))
        else:
            flash(result[1], 'danger')
    return render_template('_user/login.html', form=form)


@_user.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user_bp.login'))


@_user.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = EditForm()
    if form.validate_on_submit():
        if not validate_login_credentials(
                current_user.username,
                form.current_password.data)[0]:
            flash('Current password is not correct.', 'danger')
        try:
            update_user_with_id(
                current_user.id,
                form.first_name.data,
                form.last_name.data,
                form.email.data,
                form.username.data,
                form.new_password.data
            )
            flash('Your account information has been updated.', 'success')
        except RuntimeError as error:
            flash(str(error), 'danger')
    return render_template('_user/profile.html', form=form)

