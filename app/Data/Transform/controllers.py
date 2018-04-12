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
    delete_rows
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
    columns = []
    conditions = []
    operators = []
    logics = []
    for i in request.form:
        if i.startswith('column'):
            columns.append(i)
        elif i.startswith('condition'):
            conditions.append(i)
        elif i.startswith('logical'):
            logics.append(i)
        elif i.startswith('operator'):
            operators.append(i)
    columns.sort()
    conditions.sort()
    logics.sort()
    operators.sort()
    for i in range(len(columns)):
        if i != len(columns) - 1:
            condition += '"' + request.form[columns[i + 1]] + '"'
            if request.form[operators[i + 1]] == 'CONTAINS':
                condition += ' ~ '
            elif request.form[operators[i + 1]] == 'NOT CONTIANS':
                condition += ' !~ '
            else:
                condition += request.form[operators[i + 1]]
            condition += '\'' + request.form[conditions[i + 1]] + '\''
            condition += ' ' + request.form[logics[i]] + ' '
        else:
            condition += '"' + request.form[columns[0]] + '"'
            if request.form[operators[0]] == 'CONTAINS':
                condition += ' ~ '
            elif request.form[operators[0]] == 'NOT CONTIANS':
                condition += ' !~ '
            else:
                condition += request.form[operators[0]]
            condition += '\'' + request.form[conditions[0]] + '\''

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
    col = col[:col.find(',')]
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
