from flask import (
    Blueprint,
    request,
    jsonify,
    redirect,
    render_template,
    flash,
    Response
)
from flask_login import login_required, current_user
from app import database as db
from datatables import (
    DataTables,
    ColumnDT
)
from .operations import export_csv
from app.Project.operations import get_project_with_id
from app.Data.operations import get_dataset_with_id
from app.Data.Import.forms import UploadForm, EditForm
from app.Data.View.operations import join_datasets
from app.Data.helpers import table_name_to_object, extract_columns_from_db
from app.Data.View.operations import get_maximum_value, \
    get_minimum_value, \
    get_most_frequent_value, \
    get_number_of_null_values, \
    get_average_value



_view = Blueprint('view_bp', __name__, url_prefix='/data/view')


@_view.route('/download_csv', methods=['POST'])
@login_required
def download_csv():
    table_name = request.args.get('table_name')
    delim_char = request.form['delimiter']
    quote_char = request.form['quote']
    null_char = request.form['null']
    if table_name is None:
        flash('ERROR: No table named "{0}" found.'.format(table_name), 'danger')
        return redirect(request.referrer)
    else:
        return Response(
            export_csv(table_name, delim_char, quote_char, null_char),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=data.csv"}
        )


@_view.route('/retrieve', methods=['GET'])
@login_required
def retrieve():
    """Return server side data"""

    sql_table_name = request.args.get('sql_table_name', None)

    if sql_table_name is None:
        print(sql_table_name + " FAIL")
        return '{}'

    meta = db.MetaData(db.engine)
    table = db.Table(sql_table_name, meta, autoload=True)

    column_names = []
    for column in table.columns:
        start = str(column).find('.') + 1
        column_names.append(str(column)[start:])

    columns = []
    for name in column_names:
        statement = "columns.append(ColumnDT(table.c[\"{0}\"]))".format(name)
        exec(statement)

    # defining initial query
    query = db.session.query().select_from(table)

    # GET parameters
    params = request.args.to_dict()

    # instantiating a DataTable for the query and table needed
    rowTable = DataTables(params, query, columns)

    # returns what is needed by DataTable
    return jsonify(rowTable.output_result())


@_view.route('/join', methods=['GET', 'POST'])
@login_required
def join():

    if request.method == 'POST':
        try:
            join_datasets(request.form['file-left'],
                          request.form['column-left'],
                          request.form['file-right'],
                          request.form['column-right'],
                          request.form['join-type'],
                          request.form['join-name'],
                          request.form['join-description']
                          )
        except:
            flash('An error occured while merging datasets.', 'danger')
        else:
            flash('Datasets merged succesfully.', 'succes')
    project_id = request.args.get('project_id')
    edit_form = EditForm()
    return render_template(
        'Data/View/dataset_join.html',
        project=get_project_with_id(project_id),
        edit_form=edit_form
    )


@_view.route('/get_columns', methods=['GET'])
@login_required
def get_columns():
    dataset_id = request.args.get('dataset_id')
    dataset = get_dataset_with_id(dataset_id)

    if dataset is None:
        return '{}'

    meta = db.MetaData(db.engine)
    table = db.Table(dataset.working_copy, meta, autoload=True)

    column_names = []
    for column in table.columns:
        start = str(column).find('.') + 1
        col_name = str(column)[start:]
        if col_name != 'index':
            column_names.append(col_name)

    return jsonify(column_names)


@_view.route('/get_column_chart', methods=['GET'])
@login_required
def get_column_chart():
    dataset_id = request.args.get('dataset_id')
    column_name = request.args.get('column_name')
    stats = {}

    return jsonify(stats)


@_view.route('/get_column_info', methods=['GET'])
@login_required
def get_column_info():
    dataset = get_dataset_with_id(request.args.get('dataset_id'))
    column_name = request.args.get('column_name')
    column_type = request.args.get('column_type')

    most_freq = get_most_frequent_value(dataset.working_copy, column_name)
    nulls = get_number_of_null_values(dataset.working_copy, column_name)

    stats = {
        'Most Frequent Value': most_freq[column_name],
        'Most Frequent Value Count': most_freq['frequency'],
        'Empty Cells': nulls
    }

    if column_type in ['INTEGER', 'BIGINT', 'DOUBLE PRECISION']:
        stats['Biggest Value'] = get_maximum_value(dataset.working_copy,
                                                   column_name
                                                   )
        stats['Smallest Value'] = get_minimum_value(dataset.working_copy,
                                                    column_name
                                                    )
        stats['Average Value'] = get_average_value(dataset.working_copy,
                                                   column_name
                                                   )


    print(stats)

    return jsonify(stats)


@_view.route('/', methods=['GET'])
@login_required
def view():
    """
    Show entries of a specific table,
    or just list tables in the system if no parameter is provided
    or just list tables in the system if no parameter is provided
    """
    project_id = request.args.get('project_id', default=None)
    dataset_id = request.args.get('dataset_id', default=None)
    if dataset_id is not None:
        dataset = get_dataset_with_id(dataset_id)

        table = table_name_to_object(dataset.working_copy)

        return render_template(
            'Data/View/dataset.html',
            dataset=dataset,
            columns=extract_columns_from_db(table)
        )
    if project_id is not None:
        project = get_project_with_id(project_id)
        upload_form = UploadForm()
        edit_form = EditForm()
        return render_template(
            'Data/Import/upload.html',
            project=project,
            upload_form=upload_form,
            edit_form=edit_form
        )
    else:
        return redirect('main_bp.dashboard')


@_view.route('/raw', methods=['GET'])
@login_required
def raw():
    """
    Show entries of a specific table,
    or just list tables in the system if no parameter is provided
    """
    dataset_id = request.args.get('dataset_id', default=None)
    if dataset_id is not None:
        dataset = get_dataset_with_id(dataset_id)

        table = table_name_to_object(dataset.working_copy)

        return render_template(
            'Data/View/dataset_raw.html',
            dataset=dataset,
            columns=extract_columns_from_db(table)
        )
    else:
        return redirect('main_bp.dashboard')


@_view.route('/history', methods=['GET'])
@login_required
def history():
    dataset_id = request.args.get('dataset_id', default=None)
    if dataset_id is not None:
        dataset = get_dataset_with_id(dataset_id)
        table = table_name_to_object(dataset.working_copy)
        return render_template(
            'Data/View/dataset_history.html',
            dataset=dataset,
            columns=extract_columns_from_db(table)
        )
    else:
        return redirect('main_bp.dashboard')
