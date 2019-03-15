from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User
from app.handlers import check_field

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    #remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Register")

    def validate_username(self, field):
        username = field.data
        user = User.user_exists(username)
        if user:
            raise ValidationError("Please, use a different username")
        if not check_field(username):
            raise ValidationError("Invalid characters detected")

class AddPassword(FlaskForm):
    account = StringField('Account', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField("Submit")
