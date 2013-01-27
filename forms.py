from wtforms import Form, TextField, PasswordField, BooleanField, FloatField


class LoginForm(Form):
    """
    A form for users to login.
    """
    username = TextField('Username')
    password = PasswordField('Password')
    remember_me = BooleanField('Remember Me')


class AddUser(Form):
    """
    A form for an admin to add a user to the system
    """
    username = TextField('Username')
    password = PasswordField('Password')
    ssn = TextField('SSN')
    wage = FloatField('Hourly Wage')
    is_admin = BooleanField('Is Admin')
    is_approver = BooleanField('Is Approver')