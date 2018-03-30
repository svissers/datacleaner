from flask import Blueprint, render_template, redirect, url_for, request, flash,jsonify
from .forms import UploadForm
from .operations import upload_csv, upload_joined
from flask_login import login_required
import zipfile as zf
import os
import pprint

_upload = Blueprint('upload_bp', __name__, url_prefix='/data/upload')


@_upload.route('/', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        filename = request.files['file'].filename
        if filename.lower()[-4:] == '.csv':
            return redirect(
                url_for(
                    'upload_bp.csv',
                    project_id=request.args.get('project_id')
                ),
                code=308
            )
        elif filename.lower()[-4:] == '.zip':
            return redirect(
                url_for(
                    'upload_bp.zip',
                    project_id=request.args.get('project_id')
                        ),
                code=308
            )
        elif filename.lower()[-4:] == '.sql':
            return redirect(url_for('upload_bp.dump'), code=308)
        elif filename.lower()[-5:] == '.dump':
            return redirect(url_for('upload_bp.dump'), code=308)

    filelist = os.listdir('./file_queue/')
    for f in filelist:
        os.remove(os.path.join('./file_queue/', f))

    return redirect(url_for('main_bp.dashboard'))


@_upload.route('/csv', methods=['POST'])
@login_required
def csv():
    form = UploadForm()
    try:
        upload_csv(
            form.name.data,
            form.description.data,
            request.files['file'],
            request.args.get('project_id')
        )
    except Exception:
        flash('An error occured while uploading your file.', 'danger')
    else:
        flash('Your file has been uploaded successfully.', 'success')
    return redirect(url_for('main_bp.dashboard'))


@_upload.route('/zip', methods=['POST'])
@login_required
def zip():
    if request.files.get('file', None) is None:
        for submission in request.form:
            if submission.startswith('checkbox-'):
                filename = submission.replace('checkbox-', '')
                upload_csv(
                    request.form['name-' + filename],
                    request.form['description-' + filename],
                    './file_queue/' + filename,
                    request.args.get('project_id')
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
                    request.args.get('project_id')
                )
        flash('Your file has been uploaded.', 'success')
        return redirect(url_for('upload_bp.upload'))

    else:
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
                'Data/join_view.html',
                files=files,
                project_id=request.args.get('project_id')
            )


@_upload.route('/dump', methods=['POST'])
@login_required
def dump():
    # TODO: implement .sql/.dump upload
    return redirect(request.referrer)


@_upload.route('/extract_columns', methods=['GET'])
@login_required
def extract_columns():
    files = os.listdir('./file_queue/')
    file_to_column = {}
    for file in files:
        data = open('./file_queue/{}'.format(file), 'r')
        cscolumns = data.readline()
        columns = [x.strip() for x in cscolumns.split(',')]
        file_to_column[file] = columns
        data.close()
    return jsonify(file_to_column)
