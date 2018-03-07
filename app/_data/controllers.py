from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required
from app._data.forms import UploadForm
from app._data.models import Dataset

_data = Blueprint('data_bp', __name__, url_prefix='/data')


@_data.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        file = request.files['csvfile']
        Dataset.import_from_csv(form.name.data,
                                form.description.data,
                                file)
    return render_template('upload.html', form=form)
