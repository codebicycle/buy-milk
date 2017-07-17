from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length

from todo.models import User

class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

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
