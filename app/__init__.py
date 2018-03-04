from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Setup and config app
app = Flask(__name__)
app.config.from_object('config')

# Setup Bootstrap
Bootstrap(app)

# Setup SQLAlchemy
database = SQLAlchemy(app)

# Setup LoginManager
login_manager = LoginManager(app)

# Import user modules, needs to be after login_manager instantiation
from app._user.controllers import _user as user_module
from app._main.controllers import _main as main_module

# Register blueprints
app.register_blueprint(user_module)
app.register_blueprint(main_module)

# Build database
database.create_all()
