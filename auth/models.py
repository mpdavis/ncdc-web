import datetime

from flask_mongoengine import Document
from flask_mongoengine import DoesNotExist

from app import db


class User(Document):
    username = db.StringField(max_length=255, required=True)
    password = db.StringField(max_length=255, required=True)

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


class TimeRecord(Document):
    date = db.DateTimeField(default=datetime.date.today(), required=True)
    clock_in = db.DateTimeField(required=False)
    clock_out = db.DateTimeField(required=False)
    approved = db.BooleanField(default=False, required=True)
    approved_by = db.StringField(max_length=255, required=False)