# Todo

Create and share todo lists.  
No registration needed.

Todo is a Python web application powered by Flask.  
Demo at [buymilk.herokuapp.com](https://buymilk.herokuapp.com)


- Create todos without registering
- Share todos with friends
- Collaborate on shared todos
- Explore public todos
- Works on your phone


## Run

    export FLASK_APP=todo/__init__.py
    flask run

## Install

Set the secret key

- In a `secrets.py` file that you create. (see `secrets.py.sample`)
- Or as an environment variable. `export SECRET_KEY=`


How to generate good secret keys

    >>> import os
    >>> os.urandom(24)


Run database migrations

    flask db upgrade
