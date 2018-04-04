import os

# Statement for enabling the development environment
DEBUG = True

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define production database
# SQLAlchemy URI uses following format:
# dialect+driver://username:password@host:port/database
# Many of the parts in the string are optional.
# If no driver is specified the default one is selected
# (make sure to not include the + in that case)
SQLALCHEMY_DATABASE_URI = 'postgresql://flask:flask@localhost:5432/flask_db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True
CSRF_SESSION_KEY = 'NotSoSecret'

# Secret key for signing cookies
SECRET_KEY = 'NotSoSecret'
