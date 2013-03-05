import datetime
import utils
import crypto
import time
import re

from urlparse import urljoin
from BeautifulSoup import BeautifulSoup, Comment

from flask import url_for, request, redirect, url_for

# Helper required by Flask-Login for returning a redirect to the login page.
def user_unauthorized_callback():
    return redirect(url_for('logout'))

# Helper required by Flask-Login for returning the current user.
def load_user(username):
    from models import User
    user = User.objects.get(username=username)
    if user:
        return user
    return redirect(url_for('logout'))

# Helper method for determining the monday immediately prior to a given day.
def get_last_monday(today):
    offset = today.weekday() % 7
    last_monday = today - datetime.timedelta(days=offset)
    return last_monday

def sanitize_number_input(number):
    try:
        float(number)
        return True
    except ValueError:
        return False

def sanitize_time_input(time_input):
    try:
        time.strptime(time_input, '%I:%M %p')
        return True
    except ValueError:
        return False

def sanitize_mongo_hash(hash):
    if hash:
        if len(hash) == 24:
            return re.findall(r"([a-fA-F\d]{24})", hash)
    return False

def sanitizeHtml(value, base_url=None):
    rjs = r'[\s]*(&#x.{1,7})?'.join(list('javascript:'))
    rvb = r'[\s]*(&#x.{1,7})?'.join(list('vbscript:'))
    re_scripts = re.compile('(%s)|(%s)' % (rjs, rvb), re.IGNORECASE)
    validTags = 'p i strong b u a h1 h2 h3 pre br img'.split()
    validAttrs = 'href src width height'.split()
    urlAttrs = 'href src'.split() # Attributes which should have a URL
    soup = BeautifulSoup(value)
    for comment in soup.findAll(text=lambda text: isinstance(text, Comment)):
        # Get rid of comments
        comment.extract()
    for tag in soup.findAll(True):
        if tag.name not in validTags:
            tag.hidden = True
        attrs = tag.attrs
        tag.attrs = []
        for attr, val in attrs:
            if attr in validAttrs:
                val = re_scripts.sub('', val) # Remove scripts (vbs & js)
                if attr in urlAttrs:
                    val = urljoin(base_url, val) # Calculate the absolute url
                tag.attrs.append((attr, val))

    return soup.renderContents().decode('utf8')

def validate_ssn(ssn):
    ssn = ssn.replace('-', '')
    # this actually matches valid SSN's (too strong for CDC)
    # if re.match(r"^(?!000|666)(?:[0-6][0-9]{2}|7(?:[0-6][0-9]|7[0-2]))?(?!00)[0-9]{2}(?!0000)[0-9]{4}$", ssn):
    if re.match(r"^(?:[0-9]{3})(?:[0-9]{2})(?:[0-9]{4})$", ssn):
        return True
    else:
        return False