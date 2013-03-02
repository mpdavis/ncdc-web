from wtforms import Form, TextField, PasswordField, BooleanField, FloatField

class LoginForm(Form):
    """
    A form for users to login.
    """
    username = TextField('Username')
    password = PasswordField('Password')
    remember_me = BooleanField('Remember Me')

class ModifyUser(Form):
    username = TextField('Username')
    wage = FloatField('Hourly Wage')
    ssn = TextField('SSN')