from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, ValidationError

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=50),
        Regexp('^[a-zA-Z]+$', message="Username should only contain letters.")
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message="Invalid email format.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, max=50),
        Regexp(r'^(?=.*[A-Z])(?=.*\d)', message="Password must contain at least one uppercase letter and one number.")
    ])
    submit = SubmitField('Register')

class BugForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        Length(max=200)
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(),
        Length(min=10)
    ])
    priority = SelectField('Priority', choices=[
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High')
    ], validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved')
    ], validators=[DataRequired()])
    submit = SubmitField('Create Bug')

class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[
        DataRequired(),
        Length(min=3, max=100, message="Project name must be between 3 and 100 characters.")
    ])
    description = TextAreaField('Project Description', validators=[
        Length(max=500, message="Description must be under 500 characters.")
    ])
    submit = SubmitField('Save Project')
