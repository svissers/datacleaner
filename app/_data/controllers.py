from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app._data.forms import UploadForm, ProjectForm
from app._data.models import Dataset
from .models import Project
import pandas as pd
from app import database as db

_data = Blueprint('data_bp', __name__, url_prefix='/data')


def get_projects(description=False):
    #TODO only projects associated with user
    if description:
        return  [(p.id, p.name, p.description) for p in Project.query.order_by('id desc')]
    return  [(p.id, p.name) for p in Project.query.order_by('id')]


def get_tables(project=None):
    #TODO check if project is associated with user
    #TODO only tables associated with project
    if project == None:
        return [(t.id, t.name, t.description, t.sql_table_name, t.project_id) for t in Dataset.query]
    else:
        return [(t.id, t.name, t.description, t.sql_table_name, project) for t in Dataset.query.filter(Dataset.project_id == project)]

@_data.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    # for project in get_projects():
    #     form.project.append_entry(project)
    form.project.choices = get_projects()
    # print form.project.data
    if form.validate_on_submit():
        print form.project.data
        file = request.files['csvfile']
        Dataset.import_from_csv(form.name.data,
                                form.description.data,
                                file,
                                form.project.data)

        flash('Your csv has been uploaded.', 'success')
        # return redirect(url_for("upload"))
        print url_for('data_bp.projects', project=form.project.data)
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
        if project == None:
            #get the projects associated with this user
            projects = get_projects(True)
            return render_template("display_projects.html", projects=projects, form=form)
        else:
            #render the project requested
            tables = get_tables(project)
            project_name = Project.query.filter(Project.id==project).first().name
            return render_template("render_project.html", tables=tables, project_name=project_name)
    else:
        #create new project
        if form.validate_on_submit():
            try:
                new_project = Project(
                    form.name.data,
                    form.description.data
                )
                new_project.add_to_database()
                flash('Your project has been created.', 'success')
                return redirect(url_for('data_bp.projects'))
            except:
                flash('failed to create project.', 'failure')
                pass
        else:
            print 'test'
            projects = get_projects(True)
            return render_template("display_projects.html", projects=projects, form=form)


@_data.route('/datasets/<int:dataset>')
@_data.route('/datasets/')
@login_required
def datasets(dataset=None):
    """Show entries of a specific table, or just list tables in the system if no parameter is provided"""
    if dataset == None:
        #get the tables associated with this user
        tables = get_tables()
        return render_template("display_tables.html", tables=tables)
    else:
        #get info from requested table out of dataset table
        dataset_info = Dataset.query.filter(Dataset.id == dataset).first()
        db_engine = db.engine
        csv_dataframe = pd.read_sql_table(dataset_info.sql_table_name, db_engine)
        # print csv_dataframe
        # render the table requested
        return render_template("render_table.html", table=csv_dataframe.to_html(classes="table table-striped"))
