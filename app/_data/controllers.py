from flask import Blueprint, render_template, redirect, url_for, request, flash,jsonify
from flask_login import login_required, current_user
from app._data.forms import UploadForm, ProjectForm, ShareForm
from app._data.models import Dataset
from .models import Project
from app._user.models import User
import pandas as pd
from app import database as db
from .helpers import get_projects, create_project, get_datasets, upload_csv, table_name_to_object as tnto, share_project_with
from datatables import (
    ColumnDT,
    DataTables
)

_data = Blueprint('data_bp', __name__, url_prefix='/data')


@_data.route('/retrieve_data')
@login_required
def retrieve_data():
    """Return server side data"""

    sql_table_name = request.args.get('sql_table_name', None)

    if sql_table_name is None:
        return '{}'

    table = tnto(sql_table_name)

    column_names = []
    for column in table.columns:
        start = str(column).find('.') + 1
        column_names.append(str(column)[start:])

    columns = []
    for name in column_names:
        statement = "columns.append(ColumnDT(table.c['{0}']))".format(name)
        exec(statement)

    # defining initial query
    query = db.session.query().select_from(table)

    # GET parameters
    params = request.args.to_dict()

    # instantiating a DataTable for the query and table needed
    rowTable = DataTables(params, query, columns)

    # returns what is needed by DataTable
    return jsonify(rowTable.output_result())


@_data.route('/<int:project_id>/upload', methods=['POST'])
@login_required
def upload(project_id):
    form = UploadForm(request.form)
    if form.is_submitted():
        mimetype = str(request.files['file'].content_type)
        try:
            if mimetype == 'text/csv':
                upload_csv(
                    form.name.data,
                    form.description.data,
                    request.files['file'],
                    project_id
                )
            elif mimetype == 'application/zip':
                pass  # TODO: implement zip upload
            elif mimetype == 'application/octet-stream':
                pass  # TODO: implement .sql/.dump upload
        except Exception:
            flash('An error occured while uploading your file.', 'danger')
        flash('Your file has been uploaded!', 'success')
    return redirect(url_for('main_bp.dashboard'))


@_data.route('/new_project', methods=['POST'])
@login_required
def new_project():
    form = ProjectForm(request.form)
    if form.validate_on_submit():
        try:
            create_project(
                form.name.data,
                form.description.data,
                current_user.id
            )
            flash('New project created successfully!', 'success')
        except Exception:
            flash('Failed to create project. Please try again.', 'failure')
    return redirect(url_for('main_bp.dashboard'))


@_data.route('/share_project', methods=['POST'])
@login_required
def share_project():
    form = ShareForm()
    if form.validate_on_submit():
        submitted_user = User.get_by_name(form.username.data)
        if submitted_user is not None:
            try:
                share_project_with(
                    request.args.get('project_id'),
                    submitted_user.id
                )
                flash(
                    'The project was succesfully shared with {}.'.
                    format(form.username.data),
                    'success'
                )
            except Exception:
                flash(
                    '{} alreay has access to this project.'.
                    format(form.username.data),
                    'warning'
                )
        else:
            flash(
                'No user with username: {}.'.format(form.username.data),
                'danger'
            )
    return redirect(url_for('main_bp.dashboard'))


@_data.route('/dataset/')
@login_required
def dataset():
    """Show entries of a specific table, or just list tables in the system if no parameter is provided"""
    dataset = request.args.get('dataset', None)
    view_raw = bool(request.args.get('raw', None))
    if dataset is None:
        return redirect(url_for('main_bp.dashboard'))
    else:
        # get info from requested table out of dataset table
        dataset = int(dataset)
        dataset_info = Dataset.query.filter(Dataset.id == dataset).first()
        table = tnto(dataset_info.sql_table_name)
        column_names = []
        for column in table.columns:
            start = str(column).find('.') + 1
            column_names.append(str(column)[start:])

        if view_raw:
            # render the table requested
            return render_template(
                "_data/render_data.html",
                cnames=column_names[1:],
                dataset_info=dataset_info
            )
        else:
            return render_template(
                "_data/render_table.html",
                dataset_info=dataset_info,
                cnames=column_names,
                columns=[]
            )


@_data.route('/datasets/delete/<id>', methods=["POST"])
def delete(id):
    selected_data = request.form.getlist("data_id[]")
    dataset_info = Dataset.query.filter(Dataset.id == id).first()
    table = tnto(dataset_info.sql_table_name)
    for data in selected_data:
        table.delete(table.c.index == data).execute()
    return redirect(request.referrer)
