from flask_wtf import FlaskForm
from wtforms import StringField, FileField, TextAreaField
from wtforms.validators import InputRequired, Length, Optional


class UploadForm(FlaskForm):
    """docstring for UploadForm"""

    file = FileField('File (.csv, .zip or .dump)',
                     validators=[InputRequired()]
                     )
    name = StringField('Name', validators=[Length(max=50)])
    description = TextAreaField('Description',
                                validators=[Optional(), Length(max=255)])