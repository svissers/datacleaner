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
from app.Data.helpers import table_name_to_object, escape_quotes
from app.Data.Transform.operations import (
    restore_original,
    change_attribute_type,
    delete_rows,
    fill_null_with,
    fill_null_with_average,
    fill_null_with_median,
    rename_attribute,
    delete_attribute,
    one_hot_encode,
    normalize_attribute,
    discretize_width,
    discretize_eq_freq,
    find_replace,
    regex_find_replace,
    substring_find_replace,
    nullify_outliers,
    extract_from_date_time
)

_transform = Blueprint('transform_bp', __name__, url_prefix='/data/transform')


@_transform.route('/rename_column', methods=['POST'])
@login_required
def rename_column():
    dataset = get_dataset_with_id(request.args.get('dataset_id'))
    col = request.form['column']
    new_name = escape_quotes(request.form['new_name'])
    try:
        rename_attribute(dataset.working_copy, col, new_name)
    except:
        flash('An unexpected error occured while renaming the column', 'danger')
    else:
        flash('Column renamed successfully.', 'success')
        create_action('Renamed column {0} to {1}'.format(col, new_name), dataset.id, current_user.id)

    return redirect(request.referrer)


@_transform.route('/delete_column', methods=['POST'])
@login_required
def delete_column():
    dataset = get_dataset_with_id(request.args.get('dataset_id'))
    col = request.form['column']
    try:
        delete_attribute(dataset.working_copy, col)
    except:
        flash('Failed to delete column {0} from {1}'.format(col, dataset.working_copy), 'danger')
    else:
        flash('Column deleted successfully.', 'success')
        create_action('Deleted column {0}'.format(col), dataset.id, current_user.id)

    return redirect(request.referrer)


@_transform.route('/one_hot_encode_column', methods=['POST'])
@login_required
def one_hot_encode_column():
    dataset = get_dataset_with_id(request.args.get('dataset_id'))
    col = request.form['column']
    try:
        one_hot_encode(dataset.working_copy, col)
    except:
        flash('An unexpected error occured while one-hot-encoding column {0}'.format(col), 'danger')
    else:
        flash('Column one-hot-encoded successfully.', 'success')
        create_action('One-hot-encoded {0}'.format(col), dataset.id, current_user.id)

    return redirect(request.referrer)


@_transform.route('/normalize_column', methods=['POST'])
@login_required
def normalize_column():
    dataset = get_dataset_with_id(request.args.get('dataset_id'))
    col = request.form['column']
    try:
        normalize_attribute(dataset.working_copy, col)
    except:
        flash('An unexpected error occured while normalizing the column',
              'danger'
              )
    else:
        flash('Column normalized successfully.', 'success')
        create_action('Normalized {0}'.format(col), dataset.id, current_user.id)

    return redirect(request.referrer)


@_transform.route('/discretize_column', methods=['POST'])
@login_required
def discretize_column():
    dataset = get_dataset_with_id(request.args.get('dataset_id'))
    column = request.form['column']
    intervals = request.form['intervals']

    try:
        if intervals == 'equal-distance':
            amount = request.form['amount-dist']
            discretize_width(dataset.working_copy, column, int(amount))
        elif intervals == 'equal-frequency':
            amount = request.form['amount-freq']
            discretize_eq_freq(dataset.working_copy, column, int(amount))
        else:
            edges = str(request.form['custom-edges'])
            edges = edges.replace(' ', '')
            edge_list = edges.split(',')
            if len(edge_list) < 2:
                raise ValueError
            for i in range(len(edge_list)):
                edge_list[i] = float(edge_list[i])
            discretize_width(dataset.working_copy, column, edge_list)

    except ValueError:
        flash('Invalid list of edges provided.', 'danger')
    except:
        flash('An unexpected error occured while discretizing the column', 'danger')
    else:
        flash('Column discretized successfully.', 'success')
        create_action('column {0} discretized'.format(column), dataset.id, current_user.id)

    return redirect(request.referrer)


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
            condition += '\'' + escape_quotes(request.form[conditions[0]]) + '\''

    try:
        if delete_rows(table.name, condition) is False:
            flash('no rows found with condition {0}'.format(condition), 'warning')
        else:
            flash('successfully deleted rows using condition {0}'.format(condition), 'success')
            create_action('rows deleted with condition {0}'.format(condition), dataset.id, current_user.id)
    except:
        flash('condition "{0}" not valid'.format(condition), 'danger')

    return redirect(request.referrer)


@_transform.route('/reset', methods=['GET'])
@login_required
def reset():
    dataset = get_dataset_with_id(request.args.get('dataset_id'))
    try:
        restore_original(dataset.working_copy)
    except:
        flash('Failed to restore original', 'danger')
    else:
        flash('restored dataset to original state', 'success')
        create_action('restored dataset to original state', dataset.id, current_user.id)
    return redirect(request.referrer)


@_transform.route('/change_type', methods=['POST'])
@login_required
def change_type():
    dataset = get_dataset_with_id(request.args.get('dataset_id'))
    table = table_name_to_object(dataset.working_copy)
    col = request.form['column']
    col = col[:col.find('(') - 1]
    new_type = request.form['type']
    if col != '' and new_type != '':
        try:
            change_attribute_type(table.name, col, new_type)
        except:
            flash('{0} could not be converted to {1}'.format(col, new_type), 'danger')
        else:
            flash('{0} successfully  converted to {1}'.format(col, new_type), 'success')
            create_action('type {0} changed to {1}'.format(col, new_type), dataset.id, current_user.id)

    return redirect(request.referrer)


@_transform.route('/remove_outliers', methods=['POST'])
@login_required
def remove_outliers():
    dataset = get_dataset_with_id(request.args.get('dataset_id'))
    col = request.form['column']
    operator = request.form['outlier-operator']
    edge = escape_quotes(request.form['outlier-edge'])

    try:
        nullify_outliers(dataset.working_copy, col, edge, operator)
    except:
        flash('An unexpected error occured while removing outliers.', 'danger')
    else:
        flash('Outliers removed successfully.', 'success')
        create_action('Removed values from {0} if {1} {2}.'.format(col, operator, edge), dataset.id, current_user.id)

    return redirect(request.referrer)


@_transform.route('/find_and_replace', methods=['POST'])
@login_required
def find_and_replace():
    dataset = get_dataset_with_id(request.args.get('dataset_id'))
    col = request.form['column']
    find = escape_quotes(request.form['find'])
    match_mode = request.form['match-mode']
    replace = escape_quotes(request.form['replace'])
    try:
        if match_mode == 'full-match':
            find_replace(dataset.working_copy, col, find, replace)
        elif match_mode == 'substring-match':
            replace_mode = request.form['replace-mode']
            if replace_mode == 'full-replace':
                substring_find_replace(dataset.working_copy,
                                       col,
                                       find,
                                       replace,
                                       full=True)
            elif replace_mode == 'substring-replace':
                substring_find_replace(dataset.working_copy,
                                       col,
                                       find,
                                       replace,
                                       full=False)
        elif match_mode == 'regex-match':
            regex_find_replace(dataset.working_copy, col, find, replace)
    except:
        flash('failed to find and replace {0} with {1}'.format(find, replace), 'danger')
    else:
        flash('successfully replaced {0} with {1}'.format(find, replace), 'success')
        create_action(
            'replaced {0} with {1} in column {2}'.format(find, replace, col),
            dataset.id,
            current_user.id)
    return redirect(request.referrer)


@_transform.route('/fill_null', methods=['POST'])
@login_required
def fill_null():
    dataset = get_dataset_with_id(request.args.get('dataset_id'))
    column_and_type = request.form['column']
    column_name = column_and_type[:column_and_type.find('(')-1]
    column_type = column_and_type[column_and_type.find('(') + 1:column_and_type.rfind(')')]
    fill_value = escape_quotes(request.form['fill_value'])

    if fill_value == '~option-average~':
        if column_type not in ['INTEGER', 'DOUBLE']:
            flash('Operation not supported for this column type.', 'danger')
        else:
            try:
                fill_null_with_average(dataset.working_copy, column_name)
            except:
                flash('Failed to fill column {0} with average'.format(column_name), 'danger')
            else:
                flash('Fill operation completed successfully', 'success')
                create_action(
                    'Filled null values in {0} with average'.format(column_name),
                    dataset.id,
                    current_user.id
                )
    elif fill_value == '~option-median~':
        if column_type not in ['INTEGER', 'DOUBLE']:
            flash('Operation not supported for this column type.', 'danger')
        else:
            try:
                fill_null_with_median(dataset.working_copy, column_name)
            except:
                flash('Failed to fill column {0} with median'.format(column_name), 'danger')
            else:
                flash('Fill operation completed successfully', 'success')
                create_action(
                    'Filled null values in {0} with median'.format(column_name),
                    dataset.id,
                    current_user.id
                )
    else:
        is_text_type = column_type == 'TEXT'
        is_date_type = column_type == 'DATE' or column_type == 'TIMESTAMP'
        try:
            fill_null_with(
                dataset.working_copy,
                column_name,
                fill_value,
                is_text_type,
                is_date_type
            )
        except:
            flash('Failed to fill column {0} with {1}'.format(column_name, fill_value), 'danger')
        else:
            flash('Fill operation completed successfully', 'success')
            create_action(
                'Filled null values in {0} with {1}'.format(column_name, fill_value),
                dataset.id,
                current_user.id)

    return redirect(request.referrer)


@_transform.route('/extract', methods=['POST'])
@login_required
def extract():
    dataset = get_dataset_with_id(request.args.get('dataset_id'))
    column = request.form['column']
    part = request.form['extract']

    try:
        extract_from_date_time(dataset.working_copy, column, part)
    except:
        flash('An error occured while extracting {0} from {1}.'.format(part, column), 'danger')
    else:
        flash('Extraction successful.', 'success')
        create_action('Extract {0} from {1}'.format(part, column), dataset.id, current_user.id)

    return redirect(request.referrer)
