from wtforms import Form, TextField, PasswordField, BooleanField


class LoginForm(Form):
    username = TextField('Username')
    password = PasswordField('Password')
    remember_me = BooleanField('Remember Me')


class AddUser(Form):
    username = TextField('Username')
    password = PasswordField('Password')
    is_admin = BooleanField('Is Admin')
    is_approver = BooleanField('Is Approver')