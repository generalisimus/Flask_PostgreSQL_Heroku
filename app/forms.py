from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, Email, Length

class UserForm(FlaskForm):
    name = StringField()
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])


class TasksForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=30)])
    description = StringField('Description', validators=[DataRequired()])
    time_start = DateTimeLocalField('Time start', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    time_end = DateTimeLocalField('Time end', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
