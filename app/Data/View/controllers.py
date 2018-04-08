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
from app import database as db
from app.Data.models import Dataset, Action
from datatables import (
    DataTables,
    ColumnDT
)
from .operations import export_csv
from app.User.operations import get_user_with_id
from app.Project.operations import get_project_with_id
from app.Data.operations import get_dataset_with_id
from app.Data.Import.forms import UploadForm
from app.Data.View.operations import join_datasets


_view = Blueprint('view_bp', __name__, url_prefix='/data/view')


@_view.route('download_csv')
@login_required
def download_csv():
    table_name = request.args.get('table_name')
    delim_char = request.args.get('delim_char', ',')
    quote_char = request.args.get('quote_char', '"')
    null_char = request.args.get('null_char', '')
    if table_name is None:
        flash('ERROR: No table named "{0}" found.'.format(table_name), 'danger')
        return redirect(request.referrer)
    else:
        return Response(
            export_csv(table_name, delim_char, quote_char, null_char),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=myplot.csv"}
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
        statement = "columns.append(ColumnDT(table.c['{0}']))".format(name)
        exec(statement)

    # defining initial query
    query = db.session.query().select_from(table)

    # GET parameters
    params = request.args.to_dict()

    # instantiating a DataTable for the query and table needed
    rowTable = DataTables(params, query, columns)

    # returns what is needed by DataTable
    return jsonify(rowTable.output_result())


@_view.route('/', methods=['GET'])
@login_required
def view():
    """
    Show entries of a specific table,
    or just list tables in the system if no parameter is provided
    """
    project_id = request.args.get('project_id', default=None)
    if project_id is None:
        return redirect('main_bp.dashboard')
    else:
        project = get_project_with_id(project_id)
        upload_form = UploadForm()
        return render_template(
            'Data/Import/upload.html',
            project=project,
            upload_form=upload_form
        )


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
    return render_template(
        'Data/View/dataset_join.html',
        project=get_project_with_id(project_id)
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
            column_names.append(str(column)[start:])

    return jsonify(column_names)


@_view.route('/history', methods=['GET'])
@login_required
def history():
    dataset = request.args.get('dataset', None)
    if dataset is not None:
        # get info from requested table out of dataset table

        dataset = int(dataset)
        dataset_info = Dataset.query.filter(Dataset.id == dataset).first()
        all_actions = Action.query.filter(Action.dataset_id == dataset).order_by(Action.time.desc()).all()
        actions = []
        for action in all_actions:
            actions.append([action.time.replace(microsecond=0), action.description, get_user_with_id(action.user_id).username])

        return render_template("Data/history.html", actions=actions, dataset_info=dataset_info)
    return redirect(url_for('main_bp.dashboard'))
