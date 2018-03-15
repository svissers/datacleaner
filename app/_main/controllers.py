from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app._data.helpers import get_datasets, get_projects
from app._data.forms import UploadForm, ProjectForm

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
    datasets = get_datasets(current_user.id)

    upload_form = UploadForm()
    project_form = ProjectForm()

    return render_template(
        '_main/dashboard.html',
        projects=projects,
        datasets=datasets,
        upload_form=upload_form,
        project_form=project_form
    )
