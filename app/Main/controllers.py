from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.Data.Import.forms import UploadForm
from app.User.forms import EditForm
from app.Project.forms import ProjectForm, ShareForm
from app.Project.operations import get_all_projects_for_user

_main = Blueprint('main_bp', __name__)


@_main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.dashboard'))
    return redirect(url_for('user_bp.login'))


@_main.route('/dashboard')
@login_required
def dashboard():
    projects = get_all_projects_for_user(current_user.id)

    upload_form = UploadForm()
    project_form = ProjectForm()
    share_form = ShareForm()
    edit_form = EditForm()

    return render_template(
        'Main/dashboard.html',
        projects=projects,
        upload_form=upload_form,
        project_form=project_form,
        share_form=share_form,
        edit_form=edit_form
    )
