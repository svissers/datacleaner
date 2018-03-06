from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin

# Setup and config app
app = Flask(__name__)
app.config.from_object('config')

# Setup Bootstrap
Bootstrap(app)

# Setup SQLAlchemy
database = SQLAlchemy(app)

# Setup LoginManager
login_manager = LoginManager(app)

# Setup Admin
admin = Admin()

# Import user modules, needs to be after login_manager instantiation
from app._user.controllers import _user as user_module
from app._admin.controllers import _admin as admin_module, CustomAdminIndexView
from app._main.controllers import _main as main_module

admin.init_app(app=app, index_view=CustomAdminIndexView())

# Register blueprints
app.register_blueprint(user_module)
app.register_blueprint(admin_module)
app.register_blueprint(main_module)

# Build database
database.create_all()

# Init admin user
from app._user.models import User
User.init_admin()
