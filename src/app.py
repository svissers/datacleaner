from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from forms import LoginForm, SignUpForm
import db_manager
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user

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
            user = User(form.username)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect username or password, please try again', 'danger')
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    # Upon submission of the form it gets validated
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
    return render_template('dashboard.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    db_manager.db.create_all(app=app)
    app.run(debug=True)
