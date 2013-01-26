from flask import redirect, url_for

import datetime


def user_unauthorized_callback():
    return redirect(url_for('login'))


def load_user(username):
    from models import User
    return User.objects.get_or_404(username=username)


def check_password(raw_password, user):
    return raw_password == user.password


def get_last_monday(today):
    offset = today.weekday() % 7
    last_monday = today - datetime.timedelta(days=offset)
    return last_monday