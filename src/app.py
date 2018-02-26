from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from forms import LoginForm, SignUpForm
from db_manager import db, Account
# from login_manager import login_manager, login_required

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
db.init_app(app)
# login_manager.init_app(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # Upon submission of the form it gets validated, 
    # if it's valid and de login info is valid we redirect to the dashboard
    if form.validate_on_submit():
        if Account.validate_login_credentials(form):
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect Username or Password', 'danger')
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    # Upon submission of the form it gets validated
    if form.validate_on_submit():
        # We try to insert the provided user info into the database
        # If this is successful we redirect to the login page
        try:
            Account.create_user(form)
            flash('You have been registered and can now log in.', 'success')
            return redirect(url_for('login'))
        # If an exception occured, we print why the insert failed
        except Exception as error:
            flash(str(error), 'danger')
    return render_template('signup.html', form=form)


@app.route('/dashboard')
# @login_required
def dashboard():
    return render_template('dashboard.html')


if __name__ == '__main__':
    db.create_all(app=app)
    app.run(debug=True)
