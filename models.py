import datetime

import utils

from flask_mongoengine import Document
from flask_mongoengine import DoesNotExist
from flask_mongoengine import MultipleObjectsReturned
from mongoengine.fields import StringField, BooleanField, DateTimeField, FloatField


class User(Document):
    username = StringField(max_length=255, required=True)
    password = StringField(max_length=255, required=True)
    is_approver = BooleanField(default=False, required=False)
    is_admin = BooleanField(default=False, required=False)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    @classmethod
    def get_user_by_username(cls, username):
        try:
            user = User.objects(username=username).get()
            return user
        except DoesNotExist, e:
            return False

    @classmethod
    def delete_user(cls, username):
        try:
            user = User.objects(username=username).get()
            user.delete()
            return True
        except DoesNotExist, e:
            return False
        except MultipleObjectsReturned, e:
            # There were multiple users made with the same username.
            # Usernames should be unique, so just delete them all.
            for user in User.objects(username=username):
                user.delete()
            return True


class TimeRecord(Document):
    username = StringField(default=None, required=True)
    date = DateTimeField(default=datetime.date.today(), required=True)
    clock_in = DateTimeField(required=False)
    clock_out = DateTimeField(required=False)
    approved = BooleanField(default=False, required=True)
    approved_by = StringField(max_length=255, required=False)
    hours = FloatField()

    def set_hours(self):
        if not self.clock_in or not self.clock_out:
            return

        time_worked = self.clock_out - self.clock_in
        self.hours = time_worked.seconds / 3600.0
        return self.hours

    @classmethod
    def get_current_week(cls, username, today=datetime.date.today()):

        try:
            user = User.objects(username=username).get()
        except DoesNotExist, e:
            return

        last_monday = utils.get_last_monday(today)
        next_monday = last_monday + datetime.timedelta(days=7)
        records = TimeRecord.objects(date__gte=last_monday,
                                     date__lt=next_monday,
                                     username=username).order_by('date')
        if len(records) < 7:
            for day in xrange(7):
                date = last_monday + datetime.timedelta(days=day)
                try:
                    record = TimeRecord.objects(date=date, username=username).get()
                except DoesNotExist, e:
                    TimeRecord(date=date, username=username).save()
            records = TimeRecord.objects(date__gte=last_monday,
                                         date__lt=next_monday,
                                         username=username).order_by('date')
        return records