import datetime
import time
import logging
import json

from flask import render_template, request, redirect, url_for, session, abort

from flask.views import MethodView
import flask_login
from flask_login import login_required

import utils
import crypto
import ldap_auth
import forms
from models import User, TimeRecord

import xlwt
import StringIO
import mimetypes
from flask import Response, send_file
from werkzeug.datastructures import Headers

# A base view class to extend
class UserAwareView(MethodView):
    
    # Adds the session property to the view
    @property
    def session(self):
        return session

    # Adds the user property to the view
    @property
    def user(self):
        if not flask_login.current_user.is_anonymous():
            return flask_login.current_user._get_current_object()
        else:
            return None

    # Adds a helper function to the view to get the context
    def get_context(self, extra_ctx=None, **kwargs):
        ctx = {
            'user': self.user,
        }
        if extra_ctx:
            ctx.update(extra_ctx)
        ctx.update(kwargs)
        return ctx

# The view for the home page
class Home(UserAwareView):
    def get(self):
        context = self.get_context()
        return render_template('index.html', **context)

# The view for the about page
class About(UserAwareView):
    def get(self):
        context = self.get_context()
        return render_template('about.html', **context)

# The view for the login page
class Login(UserAwareView):
    # GET /login
    def get(self):
        context = self.get_context()
        context['form'] = forms.LoginForm()
        return render_template('login.html', **context)

    # POST /login
    def post(self):
        form = forms.LoginForm(request.form)
        authorized = False
        error = ''

        username = form.username.data
        password = form.password.data

        if form.validate():
            authorized = ldap_auth.authenticate(username, password)
            if authorized:
                # authorized via LDAP, log in session.  If database is unaware of 
                # LDAP user create a new user with username of authenticated user
                user = User.get_user_by_username(crypto.encrypt(username))
                if not user:
                    user = User(username=crypto.encrypt(username), is_admin=ldap_auth.hasMembershipWithSession(username, authorized, "TimesheetAdmin"), is_approver=ldap_auth.hasMembershipWithSession(username, authorized, "TimesheetApprover")).save()
                else:
                    user.is_approver = ldap_auth.hasMembershipWithSession(username, authorized, "TimesheetApprover")
                    user.is_admin = ldap_auth.hasMembershipWithSession(username, authorized, "TimesheetAdmin")
                    user.save()

                # free up the LDAP resources, we are done with it
                ldap_auth.unauthenticate(authorized)
                
                flask_login.login_user(user, remember=False)
                return "success"
            else:
                print "[Username: ", username, " invalid login.]"

        return "Incorrect Username or Password"

# The view for the Logout page
class Logout(UserAwareView):
    # GET /logout
    def get(self):

        logout_options = ''
        # how nice should we be about the log out process?
        if request.args.get("byebye") == "yes":
            logout_options = '?byebye=yes'

        # check logged in
        if not self.user or not self.user.username or not self.user.is_authenticated:
            return redirect('/login' + logout_options)

        flask_login.logout_user()

        return redirect('/login' + logout_options)

# The view for the payroll page
class Payroll(UserAwareView):
    # GET /payroll or /payroll/<week> or /payroll/<payroll_user>/<week>
    @login_required
    def get(self, payroll_user=None, week=None):
        # check logged in
        if not self.user or not self.user.username or not self.user.is_authenticated:
            return redirect('/logout?byebye=yes')

        # if a payroll user is specified, the logged in user must be an approver (or it must be thier own account)
        if payroll_user:
            payroll_user = crypto.encrypt(payroll_user)
            if not self.user.is_approver:
                if not payroll_user == self.user.username:
                    return redirect('/logout?byebye=yes')

        # sanitize input for week parameter
        if week:
            if not utils.sanitize_number_input(week):
                return redirect('/logout?byebye=yes')

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
            'user': self.user,
            'table_rows': records,
            'payroll_username' : payroll_user or self.user.username,
            'start_date': start_date,
            'end_date': end_date,
            'prev_timestamp': time.mktime(prev_date.timetuple()),
            'next_timestamp': time.mktime(next_date.timetuple()),
        }
        return render_template('payroll.html', **context)

    # POST /payroll or /payroll/<payroll_user> or /payroll/<week>
    @login_required
    def post(self, payroll_user=None, week=None):
        # check logged in
        if not self.user or not self.user.username or not self.user.is_authenticated:
            return redirect('/logout?byebye=yes')

        # make sure someone isn't trying to set someone else's payroll info...
        if payroll_user:
            if not payroll_user == crypto.decrypt(self.user.username):
                print "INVALID USER REQUEST: ", payroll_user
                return redirect('/logout?byebye=yes')

        # sanitize input for week parameter
        if week:
            if not utils.sanitize_number_input(week):
                print "INVALID WEEK PARAMETER: ", week
                return redirect('/logout?byebye=yes')

        for input, value in request.form.iteritems():
            if value:
                punch_type, input_id = input.split('-')

                # check punch type
                if not punch_type == 'clockin':
                    if not punch_type == 'clockout':
                        print "INVALID PUNCH TYPE: ", punch_type
                        return redirect('/logout?byebye=yes')

                # check record id input
                if not utils.sanitize_mongo_hash(input_id):
                    print "INVALID RECORD ID: ", input_id
                    return redirect('/logout?byebye=yes')

                current_record = TimeRecord.objects(id=input_id).get()

                # only update the record if the current user actually owns it
                # users can only update their own records...
                if current_record.username == self.user.username:
                    # only let the user update the record if it hasn't been approved (no after the fact modifications)
                    if not current_record.approved:

                        # check time value
                        if not utils.sanitize_time_input(value):
                            print "INVALID TIME ENTRY: ", value
                            return redirect('/logout?byebye=yes')

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
            return redirect((url_for('payroll', payroll_user=payroll_user, week=week)))
        if self.user.username:
            return redirect((url_for('payroll')))

        return redirect('/logout?byebye=yes')

# The view for the approve page
class Approve(UserAwareView):
    # GET /approve
    @login_required
    def get(self):
        # check logged in
        if not self.user or not self.user.username or not self.user.is_authenticated:
            return redirect('/logout?byebye=yes')

        # check user is an approver
        if not self.user.is_approver:
            return redirect('/logout?byebye=yes')

        context = {
            'user': self.user
        }

        records = TimeRecord.get_unapproved_records()

        context['records'] = records

        return render_template('approve.html', **context)

    # POST /approve
    # called via AJAX
    def post(self):
        # check logged in
        if not self.user or not self.user.username or not self.user.is_authenticated:
            return "error: not authenticated"

        # check user is an approver
        if not self.user.is_approver:
            return "error: permission denied"

        id = None
        if 'id' in request.form:
            approve, id = request.form['id'].split('-')
        if not id:
            return "error"

        time_record = TimeRecord.objects(id=id).get()
        time_record.approved = True
        time_record.approved_by = self.user.username
        time_record.save()

        return "success"

# The view for the export page
class Export(UserAwareView):
    # GET /export/<username>
    @login_required
    def get(self, username):
        # check logged in
        if not self.user or not self.user.username or not self.user.is_authenticated:
            return redirect('/logout?byebye=yes')

        # check user is an admin
        if not self.user.is_admin:
            return redirect('/logout?byebye=yes')

        # set the default user if /export was called
        if not username:
            username = self.user.username
        else:
            username = crypto.encrypt(username)

        days = 14
        user = User.get_user_by_username(username)

        if not user:
            abort(404)

        # create workbook
        wb = xlwt.Workbook()
        ws = wb.add_sheet('Sheet 1')

        # write user
        ws.write(0,0,'User')
        ws.write(0,1,crypto.decrypt(user.username))
       
        # write SSN
        ws.write(1,0,'SSN')
        ws.write(1,1,crypto.decrypt(user.ssn))

        # write table headers
        ws.write(3,0,'Date')
        ws.write(3,1,'Clock In')
        ws.write(3,2,'Clock Out')
        ws.write(3,3,'Approved?')
        ws.write(3,4,'Approved By')

        # write out table entries
        records = TimeRecord.get_approved_records_by_username(username, num_days=days)

        row = 4
        for record in records:
            ws.write(row,0,record.date.strftime('%B %d'))
            ws.write(row,1,record.clock_in.strftime('%I:%M %p'))
            ws.write(row,2,record.clock_out.strftime('%I:%M %p'))
            ws.write(row,3,record.approved)
            ws.write(row,4,crypto.decrypt(record.approved_by))
            row = row + 1

        # create IO buffer
        output = StringIO.StringIO()

        # save workbook into buffer
        wb.save(output)

        # reset buffer pointer and trigger response
        output.seek(0)
        return send_file(output, attachment_filename=crypto.decrypt(user.username) + ".xls", as_attachment=True)

# The view for the admin page
class Admin(UserAwareView):
    # GET /admin
    @login_required
    def get(self):
        # check logged in
        if not self.user or not self.user.username or not self.user.is_authenticated:
            return redirect('/logout?byebye=yes')

        # check user is an admin
        if not self.user.is_admin:
            return redirect('/logout?byebye=yes')

        users = User.objects().order_by('id')
        context = {
            'user' : self.user,
            'users' : users,
            'form': forms.ModifyUser()
        }

        return render_template('admin.html', **context)

    # POST /admin
    @login_required
    def post(self):
        # check logged in
        if not self.user or not self.user.username or not self.user.is_authenticated:
            return "error: permission denied"

        # check user is an admin
        if not self.user.is_admin:
            return "error: permission denied"

        form = forms.ModifyUser(request.form)
        if form.validate():
            user = User.get_user_by_username(crypto.encrypt(form.username.data))
            if user:
                if not utils.sanitize_number_input(str(form.wage.data)):
                    return "error: invalid wage"
                user.wage = crypto.encrypt(str(form.wage.data))
                if not user.ssn:
                    if not utils.validate_ssn(form.ssn.data):
                        return "error: invalid SSN"
                    user.ssn = crypto.encrypt(form.ssn.data)
                user.save()
                return "success"
            return "error: user does not exist"
        return "error: invalid input"

# The view for the api page
class API(UserAwareView):
    # GET /api
    def get(self):
        context = {
            'timestamp1' : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %p"),
            'timestamp2' : datetime.datetime.now().strftime("%H:%M:%S %p")
        }
        return render_template('api.html', **context)
