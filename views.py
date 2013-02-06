import datetime
import time
import logging
import json

from flask import render_template, request, redirect, url_for, session, abort

from flask.views import MethodView
import flask_login
from flask_login import login_required

from settings import API_SERVER

import utils
import forms
from models import User, TimeRecord


class UserAwareView(MethodView):
    """
    A base view class to extend.
    """

    @property
    def session(self):
        """
        Adds the session property to the view.
        """
        return session

    @property
    def user(self):
        """
        Adds the user property to the view.

        :returns: The currently logged in user if one exists, else None
        """
        if not flask_login.current_user.is_anonymous():
            return flask_login.current_user._get_current_object()
        else:
            return None

    def get_context(self, extra_ctx=None, **kwargs):
        """
        Adds a helper function to the view to get the context.

        :returns: The current context with the user set.
        """
        ctx = {
            'user': self.user,
        }
        if extra_ctx:
            ctx.update(extra_ctx)
        ctx.update(kwargs)
        return ctx


class Home(UserAwareView):
    """
    The view for the home page.
    """
    def get(self):
        context = self.get_context()
        context['nav'] = 'home'
        return render_template('index.html', **context)


class About(UserAwareView):
    """
    The view for the about page.
    """
    def get(self):
        context = self.get_context()
        context['nav'] = 'about'
        return render_template('about.html', **context)


class Login(UserAwareView):
    """
    The view for the login page.
    """
    def get(self):
        context = self.get_context()
        context['nav'] = 'login'
        context['form'] = forms.LoginForm()
        return render_template('login.html', **context)

    def post(self):
        form = forms.LoginForm(request.form)
        authorized = False
        error = ''

        username = form.username.data
        password = form.password.data
        remember = form.remember_me.data

        if form.validate():
            user = User.get_user_by_username(username)
            if not user:
                return "Incorrect Username"
            authorized = utils.check_password(password, user)

            if authorized:
                flask_login.login_user(user, remember=remember)
                return "success"

        return "Incorrect Password"


class Logout(UserAwareView):
    """
    The view for the logout page.
    """
    decorators = [login_required]

    def get(self):
        flask_login.logout_user()
        return redirect(url_for('login'))


class Payroll(UserAwareView):
    """
    The view for the payroll page.
    """
    def get(self, payroll_user=None, week=None):
        start_date = utils.get_last_monday(datetime.date.today())
        end_date = start_date + datetime.timedelta(days=6)
        if week:
            start_date = utils.get_last_monday(datetime.date.fromtimestamp(float(week)))
            end_date = start_date + datetime.timedelta(days=6)
            records = TimeRecord.get_current_week(payroll_user or self.user.username, start_date)
        else:
            records = TimeRecord.get_current_week(payroll_user or self.user.username)
        if not records:
            return abort(404)

        next_date = start_date + datetime.timedelta(days=7)
        prev_date = start_date - datetime.timedelta(days=7)
        context = {
            'nav':  'payroll',
            'user': self.user,
            'table_rows': records,
            'payroll_username': payroll_user or self.user.username,
            'start_date': start_date,
            'end_date': end_date,
            'prev_timestamp': time.mktime(prev_date.timetuple()),
            'next_timestamp': time.mktime(next_date.timetuple()),
        }
        return render_template('payroll.html', **context)

    def post(self, payroll_user=None, week=None):
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
        if payroll_user and week:
            return redirect((url_for('payroll',
                                     payroll_user=payroll_user,
                                     week=week)))

        return redirect(url_for('payroll'))


class Approve(UserAwareView):
    """
    The view for the approve page.
    """
    def get(self):
        context = {
            'nav': 'approve',
            'user': self.user
        }

        records = TimeRecord.get_unapproved_records()

        context['records'] = records

        return render_template('approve.html', **context)

    def post(self):
        id = None
        approver = None
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
    """
    The view for the admin page.
    """
    def get(self):
        users = User.objects()
        add_user_form = forms.AddUser()
        context = {
            'nav': 'admin',
            'users': users,
            'user': self.user,
            'form': add_user_form,
            'api_server': API_SERVER
        }
        return render_template('admin.html', **context)

    def post(self):
        if not 'username' in request.form:
            return 'error'

        user = User.get_user_by_username(request.form['username'])
        for key, value in request.form.items():
            if hasattr(user, key):
                if value == 'true':
                    value = True
                elif value == 'false':
                    value = False
                setattr(user, key, value)
            user.save()

        data = {
            'user': user,
            'api_server': API_SERVER
        }

        return render_template('admin_user_row.html', **data)


class AddUser(UserAwareView):
    """
    The AJAX endpoint for adding a user to the system.
    """
    def post(self):
        form = forms.AddUser(request.form)
        if form.validate():
            username = form.username.data
            password = form.password.data
            is_admin = form.is_admin.data
            is_approver = form.is_approver.data
            ssn = form.ssn.data
            wage = form.wage.data

            user = User(username=username,
                 password=password,
                 is_admin=is_admin,
                 is_approver=is_approver,
                 ssn=ssn,
                 wage=wage).save()

            data = {'user': user}

            return render_template('admin_user_row.html', **data)
        return 'error'


class DeleteUser(UserAwareView):
    """
    The AJAX endpoint for deleting a user from the system.
    """
    def post(self):
        username = None
        operator = None
        logging.warning(request.form)
        if 'username' in request.form:
            username = request.form['username']
        if 'operator' in request.form:
            operator = request.form['operator']
        if not username or not operator:
            return 'error'

        deleted = User.delete_user(username)
        return "done"


class GetInfo(MethodView):
    """
    The REST API endpoint for getting payroll info about a user.
    """
    def get(self, username):
        days = int(request.args.get('days', 14))

        user = User.get_user_by_username(username)
        if not user:
            abort(404)

        records = TimeRecord.get_approved_records_by_username(username, num_days=days)
        record_list = []
        for record in records:
            record_list.append({
                'date': record.date.strftime('%B %d'),
                'clock-in': record.clock_in.strftime('%I:%M %p'),
                'clock-out': record.clock_out.strftime('%I:%M %p'),
                'approved': record.approved,
                'approved-by': record.approved_by
            })

        response = {
            'username': user.username,
            'ssn': user.ssn,
            'wage': user.wage,
            'records': record_list
        }

        return json.dumps(response)


class GetUsers(MethodView):
    """
    The REST API endpoint for getting a list of users.
    """
    def get(self):
        users = User.objects()
        user_list = [user.username for user in users]
        return json.dumps({'users': user_list})

