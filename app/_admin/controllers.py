from app import admin, database
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose
from flask_admin.base import MenuLink
from app._user.models import User
from flask import Blueprint, redirect, url_for, render_template, request
from flask_login import current_user

_admin = Blueprint('admin_bp', __name__, url_prefix='/admin')

@_admin.route("/")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('user_bp.login'))
    if not current_user.admin:
        return redirect(url_for('main_bp.dashboard'))
    return render_template("_admin/index.html")

@_admin.route("/active", methods=["POST"])
def active():
    if not current_user.is_authenticated:
        return redirect(url_for('user_bp.login'))
    if not current_user.admin:
        return redirect(url_for('main_bp.dashboard'))
    active = bool(request.form.get("active", True))
    all = bool(request.form.get("active", False))
    return render_template("_admin/index.html")

@_admin.route("/admin")
def admin():
    active = bool(request.args.get("active", True))


# class CustomAdminIndexView(AdminIndexView):
#     @expose('/')
#     def index(self):
#         if not current_user.is_authenticated:
#             return redirect(url_for('user_bp.login'))
#         if not current_user.admin:
#             return redirect(url_for('main_bp.dashboard'))
#         return render_template("_admin/index.html")
#         #return super(CustomAdminIndexView, self).index()
#
#
# class UserAdminView(ModelView):
#     # Don't display the password on the list of Users
#     column_exclude_list = ('password')
#     column_searchable_list = ['first_name', 'last_name', 'organization',
#                               'email']
#     column_editable_list = ['staff', 'admin', 'disabled']
#     can_create = False
#     can_edit = False
#     can_export = True
#
#     def is_accessible(self):
#         try:
#             return current_user.admin
#         except AttributeError:
#             return False
#
#
# admin.add_view(UserAdminView(User, database.session))
#
# return_link = MenuLink(name='Return to dashboard', url='/dashboard')
# admin.add_link(return_link)
