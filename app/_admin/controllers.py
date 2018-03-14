from app import database
from app._user.models import User
from flask import (
    Blueprint,
    request,
    jsonify,
    redirect,
    url_for,
    render_template
)
from flask_login import (
    login_required,
    current_user
)
from datatables import (
    ColumnDT,
    DataTables
)
from app._admin.forms import EditForm

_admin = Blueprint('admin_bp', __name__, url_prefix='/admin')


@_admin.route('/data')
@login_required
def data():
    """Return server side data"""
    # defining columns
    columns = [
        ColumnDT(User.id),
        ColumnDT(User.first_name),
        ColumnDT(User.last_name),
        ColumnDT(User.organization),
        ColumnDT(User.email),
        ColumnDT(User.username),
        ColumnDT(User.admin),
        ColumnDT(User.disabled)
    ]

    # defining initial query
    query = database.session.query().select_from(User)

    # GET parameters
    params = request.args.to_dict()

    # instantiating a DataTable for the query and table needed
    rowTable = DataTables(params, query, columns)

    # returns what is needed by DataTable
    return jsonify(rowTable.output_result())


@_admin.route('/manage_users', methods=['GET', 'POST'])
@login_required
def manage_users():
    """If user is admin lists with user data, redirects to dashboard if not"""
    if not current_user.admin:
        return redirect(url_for('main_bp.dashboard'))

    form = EditForm()

    if form.validate_on_submit():
        if request.form["button"] == "update":
            User.update_by_id(
                form.user_id.data,
                form.first_name.data,
                form.last_name.data,
                form.organization.data,
                form.email.data,
                form.username.data,
                ""
            )
        elif request.form["button"] == "delete":
            User.query.filter_by(id=form.user_id.data).first().\
                delete_from_database()

    return render_template('_admin/manage_users.html', form=form)
