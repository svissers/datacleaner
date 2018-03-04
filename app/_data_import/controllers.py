from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required

_data_import = Blueprint('data_import', __name__, url_prefix='data')


@_data_import.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    return render_template('upload.html', form=form)
