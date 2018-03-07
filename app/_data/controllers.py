from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app._data.forms import UploadForm, ProjectForm
from app._data.models import Dataset
from .models import Project

_data = Blueprint('data_bp', __name__, url_prefix='/data')


def get_projects(description=False):
    #TODO only projects associated with user
    if description:
        return  [(p.id, p.name, p.description) for p in Project.query.order_by('id desc')]
    return  [(p.id, p.name) for p in Project.query.order_by('id')]


def get_tables(project):
    #TODO check if project is associated with user
    #TODO only tables associated with project
    return  [(t.id, t.name, t.description) for t in Table.query.order_by('id desc')]


@_data.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    # for project in get_projects():
    #     form.project.append_entry(project)
    form.project.choices = get_projects()
    # print form.project.data
    if form.validate_on_submit():
        file = request.files['csvfile']
        Dataset.import_from_csv(form.name.data,
                                form.description.data,
                                file)
    return render_template('upload.html', form=form)

@_data.route('/projects/<int:project>')
@_data.route('/projects/', methods=['GET', 'POST'])
@login_required
def projects(project=None):
    """ - Show all projects if no project is provided, else show information about that specific project
        - Create new projects and update user permissions
    """
    form = ProjectForm()
    if request.method == "GET":
        if project == None:
            #get the projects associated with this user
            projects = get_projects()
            return render_template("display_projects.html", projects=projects, form=form)
        else:
            #render the project requested
            project = {}
            return render_template("render_project.html", project=project)
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
            projects = get_projects()
            return render_template("display_projects.html", projects=projects, form=form)


@_data.route('/tables/<int:table>')
@_data.route('/tables/')
@login_required
def tables(table=None):
    """Show entries of a specific table, or just list tables in the system if no parameter is provided"""
    if table == None:
        #get the tables associated with this user
        get_tables()
        return render_template("display_tables.html", tables=tables)
    else:
        # render the table requested
        table = {}
        return render_template("render_table.html", table=table)
