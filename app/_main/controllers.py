from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app._data.helpers import get_datasets, get_projects
from app._data.forms import UploadForm, ProjectForm, ShareForm

_main = Blueprint('main_bp', __name__)


@_main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.dashboard'))
    return redirect(url_for('user_bp.login'))


@_main.route('/dashboard')
@login_required
def dashboard():
    own_projects = get_projects(current_user.id, True, True)
    shared_projects = get_projects(current_user.id, True, False)
    datasets = get_datasets(current_user.id)

    upload_form = UploadForm()
    project_form = ProjectForm()
    share_form = ShareForm()

    return render_template(
        '_main/dashboard.html',
        own_projects=own_projects,
        shared_projects=shared_projects,
        datasets=datasets,
        upload_form=upload_form,
        project_form=project_form,
        share_form=share_form
    )
