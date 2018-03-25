from flask import Blueprint, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .forms import ProjectForm, ShareForm
from app.User import get_user_with_username
from .operations import (
    create_project,
    share_project,
    update_project_with_id,
    delete_project_with_id
)


_project = Blueprint('project_bp', __name__, url_prefix='/project')


@_project.route('/create', methods=['POST'])
@login_required
def create():
    form = ProjectForm()
    if form.validate_on_submit():
        create_project(
            form.name.data,
            form.description.data,
            current_user.id
        )
        flash('New project created successfully!', 'success')
    return redirect(url_for('main_bp.dashboard'))


@_project.route('/update', methods=['POST'])
@login_required
def update():
    form = ProjectForm()
    if form.validate_on_submit():
        update_project_with_id(
            request.form['project_id'],
            form.name.data,
            form.description.data
        )
        flash('Project updated successfully!', 'success')
    return redirect(url_for('main_bp.dashboard'))


@_project.route('/delete', methods=['POST'])
@login_required
def delete():
    delete_project_with_id(
        request.args.get('project_id'),
        current_user.id
    )
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('main_bp.dashboard'))


@_project.route('/share', methods=['POST'])
@login_required
def share():
    form = ShareForm()
    if form.validate_on_submit():
        submitted_user = get_user_with_username(form.username.data)
        with_ownership = request.form['button'] == 'with_ownership'
        if submitted_user is not None:
            try:
                share_project(
                    request.args.get('project_id'),
                    submitted_user.id,
                    with_ownership
                )
                flash(
                    'The project was succesfully shared with {}.'.
                    format(form.username.data),
                    'success'
                )
            except RuntimeError:
                flash(
                    '{} already has access to this project.'.
                    format(form.username.data),
                    'warning'
                )
        else:
            flash(
                'No user with username: {}.'.format(form.username.data),
                'danger'
            )
    return redirect(url_for('main_bp.dashboard'))