import os
from flask import Flask, render_template, redirect, url_for
from flask_mongoengine import MongoEngine

from auth import initialize as auth_init

from urls import add_urls

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__, static_folder=os.path.join(PROJECT_ROOT, 'static'), static_url_path='/static')
app.config['MONGODB_DB'] = 'ncdc'
app.config['SECRET_KEY'] = 'my_super_secret_key'

db = MongoEngine(app)

auth_init(app)
add_urls(app)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
