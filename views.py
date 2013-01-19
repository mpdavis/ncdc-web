from flask import render_template, request, redirect, url_for
import flask_login

from auth import UserAwareView
from auth import utils as auth_utils



import forms
import datetime


class Home(UserAwareView):
    def get(self):
        context = {'nav': 'home'}
        return render_template('index.html', **context)


class About(UserAwareView):
    def get(self):
        context = {'nav': 'about'}
        return render_template('about.html', **context)


class Login(UserAwareView):
    def get(self):
        form = forms.LoginForm()
        context = {'form': form, 'nav': 'login'}
        return render_template('login.html', **context)

    def post(self):
        from auth import models as auth_models

        form = forms.LoginForm(request.form)
        authorized = False

        username = form.username.data
        password = form.password.data
        remember = form.remember_me.data

        if form.validate():
            user = auth_models.User.get_user_by_username(username)
            authorized = auth_utils.check_password(password, user)

            if authorized:
                flask_login.login_user(user, remember=remember)

        return redirect(url_for('payroll'))


class Payroll(UserAwareView):
    def get(self):
        import actions
        records = actions.get_time_records(username='mike')
        context = {'username': self.user.username, 'table_rows': records}
        return render_template('payroll.html', **context)

    def post(self):
        import actions
        records = actions.get_time_records(username='mike')
        context = {'username': self.user.username, 'table_rows': records}
        return render_template('payroll.html', **context)