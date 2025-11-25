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

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class BugForm(FlaskForm):
    title = StringField('Bug Title', validators=[
        DataRequired(message="Title is required."),
        Length(max=200, message="Title must be under 200 characters.")
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(message="Description is required."),
        Length(min=10, message="Description must be at least 10 characters long.")
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
    project_id = SelectField('Project', coerce=int, validators=[DataRequired()])
    assigned_to = SelectField('Assigned To', validate_choice=False)
    submit = SubmitField('Add Bug')


class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[
        DataRequired(),
        Length(min=3, max=100, message="Project name must be between 3 and 100 characters.")
    ])
    description = TextAreaField('Project Description', validators=[
        Length(max=500, message="Description must be under 500 characters.")
    ])
    submit = SubmitField('Save Project')
