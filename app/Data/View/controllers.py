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
from app.Data.operations import get_datasets
from app.Data.Import.forms import UploadForm


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
        print(sql_table_name + "FAIL")
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
    project = get_project_with_id(project_id)
    upload_form = UploadForm()
    if project_id is None:
        return redirect('main_bp.dashboard')
    else:
        return render_template(
            'Data/Import/upload.html',
            project=project,
            upload_form=upload_form
        )


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
