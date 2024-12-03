from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

# Login Form
class LoginForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired(message="Username is required"),
        ],
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message="Password is required"),
        ],
    )
    submit = SubmitField('Login')