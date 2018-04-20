from app import database
from app.User.models import User
from app.User import (
    get_user_with_id,
    update_admin_status,
    update_disabled_status,
    delete_user_with_id
)
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

# blueprint definition
_admin = Blueprint('admin_bp', __name__, url_prefix='/admin')


# routes #=====================================================================

@_admin.route('/data')
@login_required
def data():
    """Return server side data"""
    # defining columns
    columns = [
        ColumnDT(User.id),
        ColumnDT(User.first_name),
        ColumnDT(User.last_name),
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

    # Check if the current user has admin privileges
    if not current_user.admin:
        return redirect(url_for('main_bp.dashboard'))

    if request.method == 'POST':
        if request.form["operation"] == "admin":
            return redirect(url_for('admin_bp.update_admin'), code=307)
        elif request.form["operation"] == "disable":
            return redirect(url_for('admin_bp.update_disabled'), code=307)
        elif request.form["operation"] == "delete":
            return redirect(url_for('admin_bp.delete'), code=307)

    return render_template('Admin/manage_users.html')


@_admin.route('/manage_users/update_admin', methods=['POST'])
def update_admin():
    selected_user = request.form.getlist('user_id[]')
    for user in selected_user:
        admin = get_user_with_id(int(user)).admin
        update_admin_status(int(user), not bool(admin))
    return redirect(request.referrer)


@_admin.route('/manage_users/update_disabled', methods=['POST'])
def update_disabled():
    selected_user = request.form.getlist('user_id[]')
    for user in selected_user:
        disabled = get_user_with_id(int(user)).disabled
        update_disabled_status(int(user), not bool(disabled))
    return redirect(request.referrer)


@_admin.route('/manage_users/delete', methods=['POST'])
def delete():
    selected_user = request.form.getlist('user_id[]')
    for user in selected_user:
        delete_user_with_id(int(user))
    return redirect(request.referrer)
