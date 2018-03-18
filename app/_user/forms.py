from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, HiddenField
from wtforms.validators import InputRequired, Email, Length, EqualTo, Optional


class SignUpForm(FlaskForm):
    """Represents form used for user signup"""
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
    """Represents form used for user login"""
    username = StringField(
        'Username',
        validators=[InputRequired()]
    )
    password = PasswordField(
        'Password',
        validators=[InputRequired()]
    )
    remember = BooleanField('Remember me?')


class EditForm(FlaskForm):
    """Represents form used for edit user info"""
    user_id = HiddenField('', id='user_id')
    first_name = StringField(
        'First Name',
        validators=[Optional(), Length(max=25)]
    )
    last_name = StringField(
        'Last name',
        validators=[Optional(), Length(max=25)]
    )
    organization = StringField(
        'Organization',
        validators=[Optional(), Length(max=25)]
    )
    email = StringField(
        'Email',
        validators=[Optional(), Email('Invalid email'), Length(max=50)]
    )
    username = StringField(
        'Username',
        validators=[Optional(), Length(min=4, max=20)]
    )
    new_password = PasswordField(
        'New password',
        validators=[Optional(), Length(min=4, max=80)]
    )
    confirm_password = PasswordField(
        'Confirm new password',
        validators=[EqualTo('new_password')]
    )
    current_password = PasswordField(
        'Current password',
        validators=[InputRequired()]
    )
