from flask_wtf import FlaskForm, RecaptchaField
<<<<<<< HEAD
from wtforms import StringField, PasswordField, BooleanField, FileField,TextAreaField,SelectField
from wtforms.validators import InputRequired, Email, Length, EqualTo, regexp, Optional
import re
from db_manager import Account, User_access, Project, Table



class SignUpForm(FlaskForm):
    """docstring for RegistrationForm"""
    first_name = StringField(
        'First name',
        validators=[Length(max=25)]
    )
    last_name = StringField(
        'Last name',
        validators=[Length(max=25)]
    )
    organization = StringField(
        'Organization',
        validators=[Length(max=25)]
    )
    email = StringField(
        'Email',
        validators=[InputRequired(), Email('Invalid email'), Length(max=50)]
    )
    confirm_email = StringField(
        'Confirm email',
        validators=[EqualTo('email')]
    )
    username = StringField(
        'Username',
        validators=[InputRequired(), Length(min=4, max=20)]
    )
    password = PasswordField(
        'Password',
        validators=[InputRequired(), Length(min=4, max=80)]
    )
    confirm_password = PasswordField(
        'Confirm password',
        validators=[EqualTo('password')]
    )
    recaptcha = RecaptchaField()


class LoginForm(FlaskForm):
    """docstring for LoginForm"""
    username = StringField(
        'Username',
        validators=[InputRequired()]
    )
    password = PasswordField(
        'Password',
        validators=[InputRequired()]
    )
    remember = BooleanField('Remember me?')


class UploadForm(FlaskForm):
    """docstring for UploadForm"""
    #TODO get projects from db
    projects = [(0,"project 0"), (1,"project 1"), (2,"project 2")]
    # print kwargs
    project = SelectField(
        label='Project', choices=projects
    )
    table_name = StringField(
        'Table name',
        validators=[InputRequired()]
    )
    csvfile      = FileField('Upload CSV file',
                    validators=[InputRequired()]
                    # validators=[FileAllowed(["csv"])]#regexp(r'^[^\/\\]+\.(csv|CSV)$')]
                    )
    # csvfile      = FileField()
    description = TextAreaField(u'Description')

    # def validate_csv(form, field):
    #     if field.data:
    #         field.data = re.sub(r'[^a-z0-9_.-]', '_', field.data)


class EditProfileForm(FlaskForm):
    """docstring for EditProfileForm"""
    first_name = StringField(
        'First Name',
        validators=[Length(max=25)]
    )
    last_name = StringField(
        'Last name',
        validators=[Length(max=25)]
    )
    organization = StringField(
        'Organization',
        validators=[Length(max=25)]
    )
    email = StringField(
        'Email',
        validators=[Optional(), Email('Invalid email'), Length(max=50)]
    )
    username = StringField(
        'Username',
        validators=[Optional(), Length(min=4, max=20)]
    )
    password = PasswordField(
        'new Password',
        validators=[Optional(), Length(min=4, max=80)]
    )
    confirm_password = PasswordField(
        'Confirm new password',
        validators=[EqualTo('password')]
    )
    current_password = PasswordField(
        'Current password',
        validators=[InputRequired()]
    )
