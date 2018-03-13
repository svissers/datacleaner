from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app._data.forms import UploadForm, ProjectForm
from app._data.models import Dataset
from .models import Project
import pandas as pd
from app import database as db
from .helpers import get_projects, create_project, get_tables, upload_csv, table_name_to_object as tnto

_data = Blueprint('data_bp', __name__, url_prefix='/data')


@_data.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    # for project in get_projects():
    #     form.project.append_entry(project)
    form.project.choices = get_projects(current_user.id)
    # print form.project.data
    if form.validate_on_submit():
        print(form.project.data)
        file = request.files['csvfile']
        upload_csv(form.name.data,
                   form.description.data,
                   file,
                   form.project.data)

        flash('Your csv has been uploaded.', 'success')
        # return redirect(url_for("upload"))
        print(url_for('data_bp.projects', project=form.project.data))
        return redirect(url_for('data_bp.projects', project=form.project.data))
    return render_template('upload.html', form=form)


@_data.route('/projects/', methods=['GET', 'POST'])
@login_required
def projects():
    """ - Show all projects if no project is provided, else show information about that specific project
        - Create new projects and update user permissions
    """
    project = request.args.get('project', None)
    form = ProjectForm()
    if request.method == "GET":
        if project is None:
            # get the projects associated with this user
            projects = get_projects(current_user.id, True)
            return render_template("display_projects.html", projects=projects, form=form)
        else:
            # show the tables form the project requested
            tables = get_tables(current_user.id, project)
            project_name = Project.query.filter(
                Project.id == project).first().name
            return render_template("render_project.html", tables=tables, project_name=project_name)
    else:
        # create new project
        if form.validate_on_submit():
            try:
                create_project(
                    form.name.data,
                    form.description.data,
                    current_user.id
                )
                flash('Your project has been created.', 'success')
                return redirect(url_for('data_bp.projects'))
            except:
                flash('failed to create project.', 'failure')
                pass
        else:
            print('test')
            projects = get_projects(current_user.id, True)
            return render_template("display_projects.html", projects=projects, form=form)


#@_data.route('/datasets/<int:dataset>/<int:page>')
@_data.route('/datasets/')
@login_required
def datasets(dataset=None, page=1):
    """Show entries of a specific table, or just list tables in the system if no parameter is provided"""
    dataset = request.args.get('dataset', None)

    if dataset is None:
        # get the tables associated with this user
        tables = get_tables(current_user.id)
        return render_template("display_tables.html", tables=tables)
    else:
        # get info from requested table out of dataset table
        dataset = int(dataset)
        page = request.args.get('page', None)
        dataset_info = Dataset.query.filter(Dataset.id == dataset).first()
        table = tnto(dataset_info.sql_table_name)
        column_names = []
        for column in table.columns:
            start = str(column).find('.') + 1
            column_names.append(str(column)[start:])

        if page is None:
            #make statistics

            return render_template("render_table.html", dataset_info=dataset_info,cnames=column_names,columns=[])
        else:
            page = int(page)
            results_per_page = int(request.args.get('resultsperpage', 25))
            # todo, if the number of results changes, check page
            data_page = db.session.query(table).paginate(page, results_per_page, error_out=False)

            # render the table requested
            return render_template(
                "render_data.html",
                cnames=column_names,
                dataset_info=dataset_info,
                data=data_page,
                resultsperpage=results_per_page
            )
