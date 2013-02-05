import datetime

from flask import redirect, url_for


def user_unauthorized_callback():
    """
    Helper required by Flask-Login for returning a redirect to the login page.
    """
    return redirect(url_for('login'))


def load_user(username):
    """
    Helper required by Flask-Login for returning the current user.

    :param username: The username to lookup.
    """
    from models import User
    return User.objects.get_or_404(username=username)

def get_last_monday(today):
    """
    Helper method for determining the monday immediately prior to a given day.

    :param today: The day to get the prior monday for.
    """
    offset = today.weekday() % 7
    last_monday = today - datetime.timedelta(days=offset)
    return last_monday