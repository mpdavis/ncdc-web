import os
import sys
sys.path.append('/var/www/webroot')
sys.path.insert(0, '/var/www/webroot')

import crypto
import utils

from flask import Flask, render_template, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager

from utils import user_unauthorized_callback, load_user

from urls import add_urls

# Determining the project root.
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

# Creating the Flask app object
application = Flask(__name__, static_folder=os.path.join(PROJECT_ROOT, 'static'), static_url_path='/static')

# Flask config settings
# local settings
#application.config['MONGODB_DB'] = 'db_local_name'

# production
application.config['MONGODB_SETTINGS'] = {'DB': "db_production_name", 'USERNAME': "db_user", 'PASSWORD':"db_password", 'PORT': 27017}
application.config['SECRET_KEY'] = 'secret_key'
application.debug = False

# Setting up the login manager for Flask-Login
login_manager = LoginManager()
login_manager.setup_app(application)
login_manager.unauthorized_handler(user_unauthorized_callback)
login_manager.user_loader(load_user)

# Setting up the connection to the MongoDB backend.
db = MongoEngine(application)

# Add all of the url rules for the application.  Any url answered by the application must be
# mapped to a view function here.
add_urls(application)

# error pages
@application.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@application.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

def decrypt(ciphertext):
    return crypto.decrypt(ciphertext)

def encrypt(plaintext):
    return crypto.encrypt(plaintext)

def sanitize(html):
    return utils.sanitizeHtml(html)

def mask_ssn(ssn):
    if ssn:
        return '###-##-' + ssn[-4:len(ssn)]
    else:
        return ''

application.jinja_env.globals.update(decrypt=decrypt)
application.jinja_env.globals.update(encrypt=encrypt)
application.jinja_env.globals.update(sanitize=sanitize)
application.jinja_env.globals.update(mask_ssn=mask_ssn)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 80))
    application.run(host='0.0.0.0', port=port, debug=False)
