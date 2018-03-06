from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

_main = Blueprint('main_bp', __name__)


@_main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.dashboard'))
    return redirect(url_for('user_bp.login'))


@_main.route('/dashboard')
@login_required
def dashboard():
    return render_template('_main/dashboard.html')
