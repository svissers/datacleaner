from flask_wtf import FlaskForm
from wtforms import StringField, FileField, TextAreaField
from wtforms.validators import InputRequired, Length, Regexp, Optional


class UploadForm(FlaskForm):
    """docstring for UploadForm"""
    csvfile = FileField('Upload CSV file',
                        validators=[InputRequired(),
                                    Regexp('^[^/\\\\]\.csv$')])
    name = StringField('Name', validators=[Length(max=50)])
    description = TextAreaField('Description',
                                validators=[Optional(), Length(max=255)])
