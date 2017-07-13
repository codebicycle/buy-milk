# Todo

Todo is a web application written in Flask.

Demo at [buymilk.herokuapp.com](https://buymilk.herokuapp.com)

## Run

    export FLASK_APP=todo/__init__.py
    flask run

## Install

Set the secret key

- In a `secrets.py` file that you created. (see `secrets.py.sample`)
- Or as an environment variable. `export SECRET_KEY=`


How to generate good secret keys

    >>> import os
    >>> os.urandom(24)


Run database migrations

    flask db upgrade
