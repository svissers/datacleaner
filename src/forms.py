from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length, EqualTo


class SignUpForm(FlaskForm):
    """docstring for RegistrationForm"""
    first_name = StringField('First name', validators=[Length(max=25)])
    last_name = StringField('Last name', validators=[Length(max=25)])
    organization = StringField('Organization', validators=[Length(max=25)])
    email = StringField('Email', validators=[InputRequired(), Email('Invalid email'), Length(max=50)])
    confirm_email = StringField('Confirm email', validators=[EqualTo('email')])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    confirm_password = PasswordField('Confirm password', validators=[EqualTo('password')])
    recaptcha = RecaptchaField()


class LoginForm(FlaskForm):
    """docstring for LoginForm"""
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember = BooleanField('Remember me?')
