from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Email, Length


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')

class UserEditForm(FlaskForm):
    """Form for editing user profiles."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_url = StringField('(Optional) Image URL')
    header_image_url = StringField('(Optional) Cover Image URL')
    bio = TextAreaField('(Optional) Bio')
    password = PasswordField(validators=[DataRequired()])

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
