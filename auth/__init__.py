from flask import session, redirect, url_for
from flask.views import MethodView

import flask_login
from flask_login import LoginManager


def initialize(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.unauthorized_handler(user_unauthorized_callback)
    login_manager.user_loader(load_user)


def user_unauthorized_callback():
    return redirect(url_for('login'))


def load_user(username):
    from auth.models import User
    return User.objects.get_or_404(username=username)


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
