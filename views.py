import datetime

from flask import render_template, request, redirect, url_for, session
from flask.views import MethodView
import flask_login

import utils
import forms


class UserAwareView(MethodView):

    @property
    def session(self):
        return session

    @property
    def user(self):
        if not flask_login.current_user.is_anonymous():
            return flask_login.current_user._get_current_object()
        else:
            return None

    def get_context(self, extra_ctx=None, **kwargs):
        ctx = {
            'user': self.user,
        }
        if extra_ctx:
            ctx.update(extra_ctx)
        ctx.update(kwargs)
        return ctx


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
        from models import User

        form = forms.LoginForm(request.form)
        authorized = False

        username = form.username.data
        password = form.password.data
        remember = form.remember_me.data

        if form.validate():
            user = User.get_user_by_username(username)
            authorized = utils.check_password(password, user)

            if authorized:
                flask_login.login_user(user, remember=remember)

        return redirect(url_for('payroll'))


class Payroll(UserAwareView):
    def get(self):
        from models import TimeRecord
        records = TimeRecord.get_current_week('mike')
        context = {'user': self.user, 'table_rows': records}
        return render_template('payroll.html', **context)

    def post(self):
        from models import TimeRecord
        for input, value in request.form.iteritems():
            if value:
                punch_type, input_id = input.split('-')
                current_record = TimeRecord.objects(id=input_id).get()

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
        from models import TimeRecord
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
        from models import User
        users = User.objects()
        context = {'users' : users, 'current_user': self.user}
        return render_template('admin.html', **context)