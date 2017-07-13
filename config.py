import os

try:
    from todo.secrets import SECRET_KEY
except ImportError:
    if not os.environ.get('SECRET_KEY'):
        raise ValueError('Secret key not set.')


base_dir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.environ.get('SECRET_KEY') or SECRET_KEY
SQLALCHEMY_DATABASE_URI = (
	os.environ.get('DATABASE_URL') or
    'sqlite:///' + os.path.join(base_dir, 'todo', 'development.sqlite3')
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
PREFERRED_URL_SCHEME = 'https'
