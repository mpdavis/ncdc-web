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
        from auth.models import TimeRecord
        records = TimeRecord.get_current_week('mike')
        context = {'user': self.user, 'table_rows': records}
        return render_template('payroll.html', **context)

    def post(self):
        from auth import models as auth_models
        for input, value in request.form.iteritems():
            if value:
                punch_type, input_id = input.split('-')
                current_record = auth_models.TimeRecord.objects(id=input_id).get()

                try:
                    time = datetime.datetime.strptime(value, '%I:%M %p')
                    day = current_record.date
                    timestamp = datetime.datetime.combine(day, time.time())
                except ValueError, e:
                    pass

                if punch_type == 'clockin':
                    current_record.clock_in = timestamp
                else:
                    current_record.clock_out = timestamp

                if current_record.clock_in and current_record.clock_out:
                    current_record.set_hours()

                current_record.save()

        return redirect(url_for('payroll'))


class Approve(UserAwareView):
    def post(self):
        from auth.models import TimeRecord
        if 'id' in request.form:
            approve, id = request.form['id'].split('-')
        if 'approver' in request.form:
            approver = request.form['approver']
        if not id or not approver:
            return "error"

        time_record = TimeRecord.objects(id=id).get()
        time_record.approved = True
        time_record.approved_by = approver
        time_record.save()

        return approver


class Admin(UserAwareView):
    def get(self):
        from auth.models import User
        users = User.objects()
        context = {'users' : users, 'current_user': self.user}
        return render_template('admin.html', **context)