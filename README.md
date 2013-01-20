NCDC Web Box
============

This is a web application written for the 2013 Iowa State National Cyber Defense Competition.  It is purposefully written to be vulnerable to a number of attacks.

It goes without saying that this should never make it's way into any sort of production environment.

#Installation

##MongoDB

MongoDB is used as a backend datastore for the application.  MongoDB is available in most *nix distributions and can be installed on OSX via brew.

###OSX

    brew update
    brew install mongodb

###Linux

Most Linux package management systems have a package for MongoDB

##PIP Dependencies

The rest of the dependencies can all be installed via pip.  A requirements.txt is provided for easy installation.

    pip install -r requirements.txt
