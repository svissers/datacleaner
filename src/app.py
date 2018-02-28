from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from forms import LoginForm, SignUpForm, UploadForm
import db_manager
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from werkzeug import secure_filename
import os
import pandas as pd
from sqlalchemy import create_engine

# App init ####################################################################
app = Flask(__name__)
# Configuration ###############################################################
# Needed for cryptographic modules
app.config['SECRET_KEY'] = 'NotSoSecret'
# SQLAlchemy URI uses following format:
# dialect+driver://username:password@host:port/database
# Many of the parts in the string are optional.
# If no driver is specified the default one is selected
# (make sure to not include the + in that case)
app.config['SQLALCHEMY_DATABASE_URI'] \
    = 'postgresql://flask:flask@localhost:5432/flask_db'
# Init database link
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# reCAPTCHA keys
app.config['RECAPTCHA_PUBLIC_KEY'] \
    = '6LdPYUgUAAAAAInU3DELerQHnnEs-8hyYcSKYyrF'
app.config['RECAPTCHA_PRIVATE_KEY'] \
    = '6LdPYUgUAAAAABSDhKVli2MJJe4uyAVlTI2-j4ul'
# Inits #######################################################################
Bootstrap(app)
db_manager.db.init_app(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(username):
    return User(username)


class User(UserMixin):
    def __init__(self, username):
        self.id = username


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # Upon submission of the form it gets validated,
    # if it's valid and de login info is valid we redirect to the dashboard
    if form.validate_on_submit():
        if db_manager.validate_login_credentials(
                form.username.data,
                form.password.data):
            user = User(form.username.data)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect username or password, please try again', 'danger')
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    # Upon submission of the form it gets validated
    # print form.first_name.data
    if form.validate_on_submit():
        # We try to insert the provided user info into the database
        # If this is successful we redirect to the login page
        try:
            db_manager.create_user(
                form.first_name.data,
                form.last_name.data,
                form.organization.data,
                form.email.data,
                form.username.data,
                form.password.data
            )
            flash('You have been registered and can now log in.', 'success')
            return redirect(url_for('login'))
        # If an exception occurred, we print why the insert failed
        except Exception as error:
            flash(str(error), 'danger')
    return render_template('signup.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    # print current_user.id
    # print db_manager.Account.query.filter_by(username="svissers").first()
    return render_template('dashboard.html')

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    UPLOAD_PATH = './upload/'
    # form = UploadForm()
    form = UploadForm()
    # if form.csvfile.data:
    if form.validate_on_submit():
        csvfile = request.files['csvfile']
        print form.csvfile.data.filename
        # form.validate_csv(form.csvfile)
        #loads csv into pandas
        csv = pd.read_csv(csvfile)
        #saves pandas dataframe to sql
        conn = db_manager.db.engine
        csv.to_sql(name="test", con=conn, if_exists="replace")
        # save csv to a file
        # filename = secure_filename(form.csvfile.data.filename)
        # file.save(os.path.join(UPLOAD_PATH, filename))
    return render_template('upload.html', form=form)

@app.route('/browse/<int:table>')
@app.route('/browse/')
@login_required
def browse(table=None):
    if table == None:
        #get the tables associated with this user
        tables = []
        return render_template("display_tables.html", tables=tables)
    else:
        #render the table requested
        table = {}
        return render_template("render_table.html", table=table)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    db_manager.db.create_all(app=app)
    app.run(debug=True)
