from flask_wtf import FlaskForm
from wtforms import StringField, FileField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Length, Regexp, Optional


class UploadForm(FlaskForm):
    """docstring for UploadForm"""

    project = SelectField(
        label='Project',
        coerce=int
    )

    csvfile = FileField('Upload CSV file',
                        validators=[InputRequired()
                                    #, Regexp('^[^/\\\\]\.csv$')
                                    ])
    name = StringField('Name', validators=[Length(max=50)])
    description = TextAreaField('Description',
                                validators=[Optional(), Length(max=255)])

class ProjectForm(FlaskForm):
    """Represents form used for creating projecys"""
    name = StringField(
        'Project name',
        validators=[InputRequired()]
    )
    description = StringField(
        'Project description',
        validators=[InputRequired()]
    )
