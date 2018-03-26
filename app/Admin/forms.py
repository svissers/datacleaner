from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, HiddenField
from wtforms.validators import Email, Length, InputRequired, Optional


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
    email = StringField(
        'Email',
        validators=[InputRequired(), Email('Invalid email'), Length(max=50)]
    )
    username = StringField(
        'Username',
        validators=[InputRequired(), Length(min=4, max=20)]
    )
    admin = BooleanField('Admin Rights')
    disabled = BooleanField('Disabled')
