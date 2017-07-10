import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

try:
    from todo.secrets import SECRET_KEY
except ImportError:
    if not os.environ.get('SECRET_KEY'):
        raise ValueError('Secret key not set.')


APP_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL') or
    'sqlite:///' + os.path.join(APP_DIR, 'development.sqlite3')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


import todo.views
