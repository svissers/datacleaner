from flask import Blueprint, render_template, redirect, url_for, request, flash,jsonify
from .forms import UploadForm, EditForm
from .operations import upload_csv, upload_joined, update_dataset_with_id, delete_dataset_with_id
from flask_login import login_required
import zipfile as zf
import os
from app.Project.operations import get_project_with_id
from app.Data.helpers import extract_tables_from_dump
from app import database as db
from sqlalchemy.sql import text
from app.Data.models import Dataset
import pandas as pd

import re
import sys

_upload = Blueprint('upload_bp', __name__, url_prefix='/data/upload')


@_upload.route('/', methods=['GET', 'POST'])
@login_required
def upload():

    project_id = request.args.get('project_id')

    # Clear any files from previous (unfinished) uploads
    filelist = os.listdir('./file_queue/')
    for f in filelist:
        if not f.startswith('.'):
            os.remove(os.path.join('./file_queue/', f))

    form = UploadForm()
    if form.validate_on_submit():
        filename = request.files['file'].filename
        if filename.lower()[-4:] == '.csv':
            return redirect(
                url_for(
                    'upload_bp.csv',
                    project_id=project_id
                ),
                code=308
            )
        elif filename.lower()[-4:] == '.zip':
            return redirect(
                url_for(
                    'upload_bp.zip',
                    project_id=project_id
                        ),
                code=308
            )
        elif filename.lower()[-4:] == '.sql':
            return redirect(url_for('upload_bp.dump', project_id=project_id), code=308)
        elif filename.lower()[-5:] == '.dump':
            return redirect(url_for('upload_bp.dump', project_id=project_id), code=308)
        else:
            flash('Filetype not supported.', 'danger')

    return redirect(url_for('view_bp.view', project_id=project_id))


@_upload.route('/csv', methods=['POST'])
@login_required
def csv():
    form = UploadForm()
    project_id = request.args.get('project_id')
    try:
        upload_csv(
            form.name.data,
            form.description.data,
            request.files['file'],
            project_id
        )
    except Exception:
        flash('An error occured while uploading your file.', 'danger')
    else:
        flash('Your file has been uploaded successfully.', 'success')
    return redirect(url_for('view_bp.view', project_id=project_id))


@_upload.route('/zip', methods=['POST'])
@login_required
def zip():
    form = UploadForm()
    project_id = request.args.get('project_id')
    if request.files.get('file', None) is None:
        for submission in request.form:
            if submission.startswith('checkbox-'):
                filename = submission.replace('checkbox-', '')
                upload_csv(
                    request.form['name-' + filename],
                    request.form['description-' + filename],
                    './file_queue/' + filename,
                    project_id
                )
            elif submission.startswith('join-type'):
                number = submission[-1]
                upload_joined(
                    request.form[submission],
                    request.form['join-name' + number],
                    request.form['join-description' + number],
                    request.form['file-left' + number],
                    request.form['column-left' + number],
                    request.form['file-right' + number],
                    request.form['column-right' + number],
                    project_id
                )
        flash('Your file has been uploaded.', 'success')
        return redirect(url_for('upload_bp.upload', project_id=project_id))

    else:
        edit_form = EditForm()
        with zf.ZipFile(request.files['file'], 'r') as csv_zip:
            files = []
            for file in csv_zip.namelist():
                if file.find('/') == -1:
                    files.append(file)
            file_to_column = {}
            for file in files:
                csv_zip.extract(file, path='./file_queue')
                data = open('./file_queue/{}'.format(file), 'r')
                cscolumns = data.readline()
                columns = [x.strip() for x in cscolumns.split(',')]
                file_to_column[file] = columns
                data.close()

            return render_template(
                'Data/Import/zip_join.html',
                name=form.name.data,
                description=form.description.data,
                project=get_project_with_id(project_id),
                files=files,
                edit_form=edit_form
            )


@_upload.route('/dump', methods=['POST'])
@login_required
def dump():
    # TODO: implement .sql/.dump upload
    form = UploadForm()
    project_id = request.args.get('project_id')
    print project_id
    name = form.name.data
    description = form.description.data
    file = request.files['file'].read()
    #tabledict: contains table names in dump as keys, newly generated, non overlapping names as values
    tabledict = extract_tables_from_dump(file)
    for old_table_name in tabledict:
        file = re.sub(old_table_name, tabledict[old_table_name], file)
    file = re.sub('`', '', file)
    # file = re.sub('auto_increment', 'serial', file)
    # file =  re.sub(r'int ?\([\d]+\)', "int", file, flags=re.IGNORECASE)
    # file =  re.sub(r'mediumtext', "text", file, flags=re.IGNORECASE)
    # file =  re.sub(r'[^\) ?];', "", file, flags=re.IGNORECASE)
    try:
        statement = str(file)#.decode("utf-8")
        result = db.session.execute(statement)
        db.session.commit()
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise

    for old_table_name in tabledict:
        table_name = tabledict[old_table_name]
        original = table_name
        working_copy = "wc" + table_name[2:]
        #result = s.execute('SELECT * FROM my_table WHERE my_column = :val', {'val': 5})
        connection = db.session.connection()

        # statement = text('ALTER TABLE :name RENAME TO :og')
        # print statement
        # result = db.engine.execute(statement, {'name':table_name, 'og':original})

        # connection.execute(statement, {'name':table_name, 'og':original})
        # db.session.commit()
        # connection.execute(text('CREATE TABLE :wc AS TABLE :og'), {'wc':working_copy, 'og':original})
        dataframe = pd.read_sql_table(original, db.engine)
        dataframe.to_sql(name=original, con=db.engine, if_exists="replace")
        dataframe.to_sql(name=working_copy, con=db.engine, if_exists="replace")

        # db.session.execute(text('alter table '+original+' drop constraint '+original+'_pkey'))
        # db.session.execute(text('CREATE TABLE '+working_copy+' AS TABLE '+original))#, {'wc':working_copy, 'og':original})
        # db.session.commit()
        # db.session.execute(text('ALTER TABLE '+working_copy+' ADD COLUMN index SERIAL PRIMARY KEY;'))
        # db.session.execute(text('ALTER TABLE '+original+' ADD COLUMN index SERIAL PRIMARY KEY;'))
        # db.session.commit()

        # result_dataframe.to_sql(name=original, con=db_engine, if_exists="fail")
        # result_dataframe.to_sql(name=working_copy, con=db_engine, if_exists="fail")

        new_dataset = Dataset(
            name,
            original,
            working_copy,
            description,
            project_id
        )
        db.session.add(new_dataset)
        db.session.commit()

    #TODO give user interface with option to join tables, do that and then delete the table you just created
    #extract columns

    return redirect(request.referrer)


@_upload.route('/update', methods=['POST'])
@login_required
def update():
    form = EditForm()
    if form.validate_on_submit():
        update_dataset_with_id(
            request.form['dataset_id'],
            form.name.data,
            form.description.data
        )
        flash('Project updated successfully!', 'success')
    return redirect(request.referrer)


@_upload.route('/delete', methods=['POST'])
@login_required
def delete():
    delete_dataset_with_id(
        request.form['dataset_id']
    )
    flash('Project deleted successfully!', 'success')
    return redirect(request.referrer)


@_upload.route('/extract_columns', methods=['GET'])
@login_required
def extract_columns():
    files = os.listdir('./file_queue/')
    file_to_column = {}
    for file in files:
        data = open('./file_queue/{}'.format(file), 'r')
        cscolumns = data.readline()
        columns = [x.strip('\"').strip('\'') for x in cscolumns.split(',')]
        file_to_column[file] = columns
        data.close()
    return jsonify(file_to_column)
