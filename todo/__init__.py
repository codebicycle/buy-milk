import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from todo.secrets import SECRET_KEY


APP_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL') or
    'sqlite:///' + os.path.join(APP_DIR, 'development.sqlite3')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


import todo.views
