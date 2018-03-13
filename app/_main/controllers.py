from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app._data.helpers import get_tables, get_projects

_main = Blueprint('main_bp', __name__)


@_main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.dashboard'))
    return redirect(url_for('user_bp.login'))


@_main.route('/dashboard')
@login_required
def dashboard():
    projects = get_projects(current_user.id, True)
    tables = get_tables(current_user.id)
    projects = projects[:min(len(projects), 5)]
    tables = tables[:min(len(tables), 5)]
    return render_template('_main/dashboard.html', projects=projects, tables=tables)
