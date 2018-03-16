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

    # Check if the current user has admin privileges
    if not current_user.admin:
        return redirect(url_for('main_bp.dashboard'))

    # defining initial form
    form = EditForm()

    # check if form input is valid
    if form.validate_on_submit():
        # check if update button was pressed
        if request.form["button"] == "update":
            User.update_by_id(
                form.user_id.data,
                form.first_name.data,
                form.last_name.data,
                form.organization.data,
                form.email.data,
                form.username.data,
                "",
                form.admin.data,
                form.disabled.data,
                True
            )
        # check if delete button was pressed
        elif request.form["button"] == "delete":
            User.query.filter_by(id=form.user_id.data).first().\
                delete_from_database()

    return render_template('_admin/manage_users.html', form=form)


@_admin.route('/manage_users/update_admin', methods=['POST'])
def update_admin():
    selected_user = request.form.getlist('user_id[]')
    for user in selected_user:
        admin = User.get_by_id(int(user)).admin
        User.update_admin_by_id(int(user), not bool(admin))
    return redirect(request.referrer)


@_admin.route('/manage_users/update_disabled', methods=['POST'])
def update_disabled():
    selected_user = request.form.getlist('user_id[]')
    for user in selected_user:
        disabled = User.get_by_id(int(user)).disabled
        User.update_disabled_by_id(int(user), not bool(disabled))
    return redirect(request.referrer)
