from flask import (
    Blueprint,
    request,
    jsonify,
    redirect,
    url_for,
    render_template,
    flash,
    Response
)
from flask_login import login_required, current_user
from app.Data.operations import create_action, get_dataset_with_id
from app.Data.helpers import table_name_to_object
from app.Data.Transform.operations import (
    restore_original,
    change_attribute_type
)

_transform = Blueprint('transform_bp', __name__, url_prefix='/data/transform')


@_transform.route('/delete_selection', methods=['POST'])
@login_required
def delete_selection():
    dataset = get_dataset_with_id(request.args.get('dataset_id'))
    selected_data = request.form.getlist("data_id")
    table = table_name_to_object(dataset.working_copy)
    for data in selected_data:
        table.delete(table.c.index == data).execute()
    create_action(
        'deleted selected items',
        dataset.id,
        current_user.id
    )
    return redirect(request.referrer)


@_transform.route('/reset', methods=['GET'])
@login_required
def reset():
    dataset = get_dataset_with_id(request.args.get('dataset_id'))
    restore_original(dataset.working_copy)
    create_action(
        'restored dataset to original state',
        dataset.id,
        current_user.id
    )
    return redirect(request.referrer)


@_transform.route('/change_type', methods=['POST'])
@login_required
def change_type():
    dataset = get_dataset_with_id(request.args.get('dataset_id'))
    table = table_name_to_object(dataset.working_copy)
    col = request.form['column']
    col = col[:col.find(',')]
    new_type = request.form['type']
    if col != '' and new_type != '':
        try:
            change_attribute_type(table.name, col, new_type)
            create_action('type {0} changed to {1}'.format(col, new_type), dataset.id, current_user.id)
        except:
            flash('{0} could not be converted to {1}'.format(col, new_type), 'danger')
        else:
            flash('{0} successfully  converted to {1}'.format(col, new_type), 'succes')

    return redirect(request.referrer)
