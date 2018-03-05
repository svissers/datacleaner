from app import admin, database
from flask_admin.contrib.sqla import ModelView
from app._user.models import User
from flask import Blueprint

_admin = Blueprint('admin_bp', __name__)


class UserAdminView(ModelView):

    # Don't display the password on the list of Users
    column_exclude_list = ('password')
    column_searchable_list = ['first_name', 'last_name', 'email']
    column_editable_list = ['staff', 'admin', 'disabled']
    can_create = False
    can_edit = False
    can_export = True


admin.add_view(UserAdminView(User, database.session))
