from app import login_manager as lm
from .models import User
from .forms import SignUpForm, LoginForm, EditForm
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user


_user = Blueprint('user_bp', __name__, url_prefix='/user')
lm.login_view = 'user_bp.login'


@lm.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@_user.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        try:
            new_user = User(
                form.first_name.data,
                form.last_name.data,
                form.organization.data,
                form.email.data,
                form.username.data,
                form.password.data
            )
            new_user.add_to_database()
            flash('You have been registered and can now log in.', 'success')
            return redirect(url_for('user_bp.login'))
        except Exception as error:
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
            user = User.get_by_name(form.username.data)
            login_user(user)
            return redirect(url_for('user_bp.profile'))
        else:
            flash(result[1], 'danger')
    return render_template('_user/login.html', form=form)


@_user.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user_bp.login'))


@_user.route('/profile')
@login_required
def profile():
    user = User.get_by_id(current_user.id)
    info = {'username': user.username,
            'email': user.email,
            'fname': user.first_name,
            'lname': user.last_name,
            'organization': user.organization}
    return render_template('_user/profile.html', info=info)


@_user.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = User.get_by_id(current_user.id)
    info = {'username': user.username,
            'email': user.email,
            'fname': user.first_name,
            'lname': user.last_name,
            'organization': user.organization,
            'password': user.password,
            'id': user.id}

    form = EditForm()
    if form.validate_on_submit():
        if not User.validate_login_credentials(info['username'],
                                               form.current_password.data):
            flash('Current password is not correct.', 'danger')
            return render_template('edit_profile.html', info=info, form=form)
        try:
            print(info['id'])
            User.update_by_id(
                info['id'],
                form.first_name.data,
                form.last_name.data,
                form.organization.data,
                form.email.data,
                form.username.data,
                form.password.data
            )
            flash('Your account information has been updated.', 'success')
            return redirect(url_for('user_bp.profile'))
        except Exception as error:
            flash(str(error), 'danger')
    return render_template('_user/edit_profile.html', info=info, form=form)
