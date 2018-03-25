from flask import Blueprint, render_template, redirect, url_for, request, flash,jsonify
from .forms import UploadForm
from .operations import upload_csv
from flask_login import login_required
import zipfile as zf
import os

_upload = Blueprint('upload_bp', __name__, url_prefix='/data/upload')


@_upload.route('/', methods=['POST'])
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
            return redirect(url_for('upload_bp.zip'), code=308)
        elif filename.lower()[-4:] == '.sql':
            return redirect(url_for('upload_bp.dump'), code=308)
        elif filename.lower()[-5:] == '.dump':
            return redirect(url_for('upload_bp.dump'), code=308)

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
    return redirect(request.referrer)


@_upload.route('/zip', methods=['POST'])
@login_required
def zip():
    # TODO: redo .zip upload
    return redirect(request.referrer)


@_upload.route('/dump', methods=['POST'])
@login_required
def dump():
    # TODO: implement .sql/.dump upload
    return redirect(request.referrer)


# @_upload.route('/<int:project_id>/upload', methods=['POST'])
# @login_required
# def upload(project_id):
#     form = UploadForm()
#     if form.validate_on_submit():
#         mimetype = str(request.files['file'].content_type)
#         try:
#             if mimetype == 'text/csv':
#                 upload_csv(
#                     form.name.data,
#                     form.description.data,
#                     request.files['file'],
#                     project_id
#                 )
#             elif mimetype == 'application/zip':
#                 with zf.ZipFile(request.files['file'], 'r') as csv_zip:
#                     files = []
#                     for file in csv_zip.namelist():
#                         if file.find('/') == -1:
#                             files.append(file)
#                     # list all possible join combinations
#                     table_combinations = []
#                     for first in range(0, len(files)-1):
#                         for second in range(first+1, len(files)):
#                             table_combinations.\
#                                 append((files[first], files[second]))
#
#                     # map filename to column name
#                     file_to_column = {}
#                     for file in files:
#                         csv_zip.extract(file, path='./file_queue')
#                         data = open('./file_queue/{}'.format(file), 'r')
#                         cscolumns = data.readline()
#                         columns = [x.strip() for x in cscolumns.split(',')]
#                         file_to_column[file] = columns
#                         data.close()
#
#                     return render_template(
#                         'Data/join_view.html',
#                         join_combinations=table_combinations,
#                         file_to_column=file_to_column,
#                         project_id=project_id,
#                         data_name=form.name.data,
#                         data_description=form.description.data
#                     )
#             elif mimetype == 'application/octet-stream':
#                 pass  # TODO: implement .sql/.dump upload
#         except Exception:
#             flash('An error occured while uploading your file.', 'danger')
#         flash('Your file has been uploaded!', 'success')
#     return redirect(url_for('main_bp.dashboard'))