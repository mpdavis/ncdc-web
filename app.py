import os
import sys
from flask import Flask, render_template, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager

from utils import user_unauthorized_callback, load_user

from urls import add_urls

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__, static_folder=os.path.join(PROJECT_ROOT, 'static'), static_url_path='/static')
app.config['MONGODB_DB'] = 'ncdc'
app.config['SECRET_KEY'] = 'my_super_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.unauthorized_handler(user_unauthorized_callback)
login_manager.user_loader(load_user)

db = MongoEngine(app)

app.debug = True
#toolbar = DebugToolbarExtension(app)
add_urls(app)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
