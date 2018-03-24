from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import sys

# Setup and config app
app = Flask(__name__)

# Setup correct database configurations
if len(sys.argv) == 2:
    app.config.from_object('config')
else:
    app.config.from_object('config_tests')

# Setup Bootstrap
Bootstrap(app)

# Setup SQLAlchemy
database = SQLAlchemy(app)

# Setup LoginManager
login_manager = LoginManager(app)

# Import user modules, needs to be after login_manager and database instantiation
from app.User.controllers import _user as user_module
from app.Admin.controllers import _admin as admin_module
from app.Main.controllers import _main as main_module
from app.Data.controllers import _data as data_module

# admin.init_app(app=app)#, index_view=CustomAdminIndexView())

# Register blueprints
app.register_blueprint(user_module)
app.register_blueprint(admin_module)
app.register_blueprint(main_module)
app.register_blueprint(data_module)

# Build database
database.create_all()

# Init admin user
from app.User.models import User
User.init_admin()
