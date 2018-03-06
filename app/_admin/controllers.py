from app import admin, database
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose
from flask_admin.base import MenuLink
from app._user.models import User
from flask import Blueprint, redirect, url_for
from flask_login import current_user

_admin = Blueprint('admin_bp', __name__)


class CustomAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('user_bp.login'))
        if not current_user.admin:
            return redirect(url_for('main_bp.dashboard'))
        return super(CustomAdminIndexView, self).index()


class UserAdminView(ModelView):
    # Don't display the password on the list of Users
    column_exclude_list = ('password')
    column_searchable_list = ['first_name', 'last_name', 'email']
    column_editable_list = ['staff', 'admin', 'disabled']
    can_create = False
    can_edit = False
    can_export = True

    def is_accessible(self):
        try:
            return current_user.admin
        except AttributeError:
            return False


admin.add_view(UserAdminView(User, database.session))

return_link = MenuLink(name='Return to dashboard', url='/dashboard')
admin.add_link(return_link)
