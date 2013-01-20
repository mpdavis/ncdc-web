from flask import redirect, url_for


def user_unauthorized_callback():
    return redirect(url_for('login'))


def load_user(username):
    from models import User
    return User.objects.get_or_404(username=username)


def check_password(raw_password, user):
    return raw_password == user.password