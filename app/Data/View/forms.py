from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired, Length


class DeleteForm(FlaskForm):
    """Represents form used for sharing projects"""
    condition = StringField(
        '',
        id='condition',
        validators=[InputRequired()]
    )