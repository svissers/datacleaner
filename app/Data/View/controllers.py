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
from app.Data.helpers import table_name_to_object
from datatables import (
    DataTables,
    ColumnDT
)
from .operations import export_csv
from .forms import DeleteForm
from app.Data.Transform.operations import change_attribute_type, delete_rows
from app.Data.operations import create_action
from app.User.operations import get_user_with_id


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


@_view.route('/', methods=['GET', 'POST'])
@login_required
def view():
    """
    Show entries of a specific table,
    or just list tables in the system if no parameter is provided
    """
    dataset = request.args.get('dataset', None)
    view_raw = bool(request.args.get('raw', None))
    change_type = bool(request.args.get('change_type', None))
    delete = bool(request.args.get('delete', None))
    delete_selection = bool(request.args.get('delete_selection', None))
    if dataset is None:
        return redirect(url_for('main_bp.dashboard'))
    else:
        # get info from requested table out of dataset table
        dataset = int(dataset)
        dataset_info = Dataset.query.filter(Dataset.id == dataset).first()
        table = table_name_to_object(dataset_info.working_copy)
        if change_type:
            col = request.form['column']
            new_type = request.form['type']
            if col != '' and new_type != '':
                try:
                    change_attribute_type(table.name, col, new_type)
                    create_action('type {0} changed to {1}'.format(col, new_type), dataset, current_user.id)
                except:
                    flash('{0} could not be converted to {1}'.format(col, new_type), 'danger')

        if delete:
            condition = ''
            for i in request.form:
                print(i)
                print(request.form[i])
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
                create_action('rows deleted with condition "{0}"'.format(condition), dataset, current_user.id)
            except:
                flash('condition "{0}" not valid'.format(condition), 'danger')
        if delete_selection:
            selected_data = request.form.getlist("data_id[]")
            for data in selected_data:
                table.delete(table.c.index == data).execute()
            create_action('deleted selected items', dataset, current_user.id)
        column_data = []
        table = table_name_to_object(dataset_info.working_copy)
        for column in table.columns:
            # change_column_type(table.name, column.name, 'integer')
            start = str(column).find('.') + 1
            column_data.append([str(column)[start:], column.type, 'b'])

        if view_raw:
            # render the table requested
            return render_template(
                "Data/render_data.html",
                cnames=column_data[1:],
                dataset_info=dataset_info,
            )
        else:
            return render_template(
                "Data/render_table.html",
                dataset_info=dataset_info,
                cnames=column_data,
                columns=[]
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
