NCDC Web Box
============

This is a web application written for the 2013 Iowa State National Cyber Defense Competition.  It is purposefully written to be vulnerable to a number of attacks.

It goes without saying that this should never make it's way into any sort of production environment.

#Installation

##MongoDB

MongoDB is used as a backend datastore for the application.

###Ubuntu

Python LDAP
`sudo apt-get install python-ldap`

Mongo

Follow steps on: http://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/

then run:

`sudo apt-get install mongodb-10gen`
`sudo service mongodb restart`

--Flask--
`sudo apt-get install python-virtualenv`
`sudo apt-get install build-essential python-dev`

The rest of the dependencies can all be installed via pip.  A requirements.txt is provided for easy installation.

`sudo pip install -r requirements.txt`

To Run (in development mode)
`sudo python app.wsgi`

Production mode was run in Apache 2.2 with mod_wsgi, mod_python, mod_security, and mod_evasion.
