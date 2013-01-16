from wtforms import Form, TextField, PasswordField, BooleanField


class LoginForm(Form):
    username = TextField('Username')
    password = PasswordField('Password')
    remember_me = BooleanField('Remember Me')