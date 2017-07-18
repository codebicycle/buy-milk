from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import (InputRequired, Length, EqualTo, Email, Optional,
    DataRequired)

from todo.models import User

class LoginForm(FlaskForm):
    email = StringField('email', validators=[
        InputRequired(),
        Length(max=255),
        Email(),
    ])
    password = PasswordField('password', validators=[
        InputRequired(),
        Length(max=255),
    ])

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        is_valid = FlaskForm.validate(self)
        if not is_valid:
            return False

        email = self.email.data.lower()
        password = self.password.data
        user = User.query.filter_by(email=email).first()
        if user is None or not user.is_valid_password(password):
            self.password.errors.append('Email is not registered or password does not match.')
            return False

        self.user = user
        return True


class RegisterForm(FlaskForm):
    email = StringField('email', validators=[
        InputRequired(),
        Length(max=255),
        Email(),
    ])
    password = PasswordField('password', validators=[
        InputRequired(),
        Length(min=3, max=255),
    ])
    confirm = PasswordField('Repeat password', validators=[
        InputRequired(),
        Length(max=255),
        EqualTo('password', message='Passwords must match.'),
    ])

    def validate(self):
        is_valid = FlaskForm.validate(self)
        if not is_valid:
            return False

        email = self.email.data.lower()
        user = User.query.filter_by(email=email).first()
        if user:
            self.email.errors.append('An account using this email is already registered.')
            return False

        return True


class TodoNewForm(FlaskForm):
    title = StringField('title', validators=[Length(max=255)])
    task = StringField('task', validators=[
        DataRequired(),
        Length(max=255)
    ])
