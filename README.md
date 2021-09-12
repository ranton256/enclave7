This is the Enclave7 project.

# Overview
Enclave7 is a web app that lets you post messages and images to a shared board where other users can see.

# Status
So far we have support for user registration, login, and ability to post an view messages and images.

# First Time Development Setup

Setup a python virtual environment if you have not already.

    python -mvenv .venv

Activate your virtual environment on Linux or Mac like this:
You have to do this each time.

	source .venv/bin/activate

Install the requirements with pip.

   pip install -r requirements.txt


Setup the local SQLite development database.

    flask db upgrade

You also need to do this whenever the database tables/schema change.
