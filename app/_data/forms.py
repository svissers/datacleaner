from flask_wtf import FlaskForm
from wtforms import StringField, FileField, TextAreaField, IntegerField
from wtforms.validators import InputRequired, Length, Optional


class UploadForm(FlaskForm):
    """docstring for UploadForm"""

    file = FileField('File (.csv, .zip or .dump)',
                     validators=[InputRequired()])
    name = StringField('Name', validators=[Length(max=50)])
    description = TextAreaField('Description',
                                validators=[Optional(), Length(max=255)])


class ProjectForm(FlaskForm):
    """Represents form used for creating projecys"""
    name = StringField(
        'Project name',
        validators=[InputRequired()]
    )
    description = TextAreaField(
        'Project description',
        validators=[InputRequired(), Length(max=255)]
    )


class ShareForm(FlaskForm):
    """Represents form used for sharing projects"""
    username = StringField(
        '',
        id='username',
        validators=[InputRequired()]
    )

