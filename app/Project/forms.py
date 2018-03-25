from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired, Length


class ProjectForm(FlaskForm):
    """Represents form used for creating projects"""
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