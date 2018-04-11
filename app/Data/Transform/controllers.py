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
    change_attribute_type,
    delete_rows,
    fill_null_with,
    fill_null_with_average,
    fill_null_with_median
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


@_transform.route('/delete_predicate', methods=['POST'])
@login_required
def delete_predicate():
    dataset = get_dataset_with_id(request.args.get('dataset_id'))
    table = table_name_to_object(dataset.working_copy)
    condition = ''
    for i in request.form:
        if i.startswith('column'):
            condition += '"' + request.form[i] + '"'
        elif i.startswith('condition'):
            condition += '\'' + request.form[i] + '\''
        elif i.startswith('logical'):
            condition += ' ' + request.form[i] + ' '
        elif i.startswith('operator') and request.form[i] == 'CONTAINS':
            condition += ' ~ '
        elif i.startswith('operator') and request.form[i] == 'NOT CONTAINS':
            condition += ' !~ '
        else:
            condition += request.form[i]
    try:
        delete_rows(table.name, condition)
        create_action('rows deleted with condition "{0}"'
                      .format(condition), dataset.id, current_user.id
                      )
    except:
        flash('condition "{0}" not valid'.format(condition), 'danger')
    else:
        flash('successfully deleted rows using condition "{0}"'
              .format(condition), 'success'
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
    col = col[:col.find(' ')]
    new_type = request.form['type']
    if col != '' and new_type != '':
        try:
            change_attribute_type(table.name, col, new_type)
            create_action('type {0} changed to {1}'.format(col, new_type), dataset.id, current_user.id)
        except:
            flash('{0} could not be converted to {1}'.format(col, new_type), 'danger')
        else:
            flash('{0} successfully  converted to {1}'.format(col, new_type), 'success')

    return redirect(request.referrer)


@_transform.route('/fill_null', methods=['POST'])
@login_required
def fill_null():
    dataset = get_dataset_with_id(request.args.get('dataset_id'))
    column_and_type = request.form['column']
    column_name = column_and_type[:column_and_type.find(' ')]
    column_type = column_and_type[column_and_type.find('(')+1:column_and_type.rfind(')')]
    fill_value = request.form['fill_value']

    try:
        if fill_value == '~option-average~':
            if column_type not in ['INTEGER', 'BIGINT', 'DOUBLE PRECISION']:
                flash('Operation not supported for this column type.', 'danger')
            else:
                fill_null_with_average(dataset.working_copy, column_name)
                create_action(
                    'Filled null values in {0} with average'.format(column_name),
                    dataset.id,
                    current_user.id
                )
        elif fill_value == '~option-median~':
            if column_type not in ['INTEGER', 'BIGINT', 'DOUBLE PRECISION']:
                flash('Operation not supported for this column type.', 'danger')
            else:
                fill_null_with_median(dataset.working_copy, column_name)
                create_action(
                    'Filled null values in {0} with median'.format(column_name),
                    dataset.id,
                    current_user.id
                )
        else:
            is_text_type = column_type in ['TEXT',
                                           'VARCHAR(10)',
                                           'VARCHAR(25)',
                                           'VARCHAR(255)']
            fill_null_with(
                dataset.working_copy,
                column_name,
                fill_value,
                is_text_type
            )
            create_action(
                'Filled null values in {0} with {1}'
                .format(column_name, fill_value),
                dataset.id,
                current_user.id
            )
    except:
        flash(
            'An unexpected error occured while performing the operation',
            'danger'
            )
    else:
        flash('Fill operation completed successfully', 'success')

    return redirect(request.referrer)
