import base64
from datetime import datetime
import os

import bcrypt
from flask import (Flask, render_template, request, session, redirect, url_for,
                   flash, abort)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from secrets import SECRET_KEY


app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/development.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password_hash = db.Column(db.Binary(60))
    todos = db.relationship('Todo', backref='user', lazy='dynamic')

    def __init__(self, email, password):
        self.email = email.lower()
        self.password_hash = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

    def is_valid_password(self, password):
        return bcrypt.checkpw(password.encode('utf8'), self.password_hash)

    def __repr__(self):
        return '<User {}>'.format(self.email)


class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    private = db.Column(db.Boolean)
    date_created = db.Column(db.DateTime)
    tasks = db.relationship('Task', backref='todo', lazy='select')


    def __init__(self, title, user_id, private=False):
        self.title = title
        self.user_id = user_id
        self.private = private
        self.date_created = datetime.utcnow()

    def __repr__(self):
        return '<Todo {}>'.format(self.title)


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    done = db.Column(db.Boolean)
    date_completed = db.Column(db.DateTime)
    todo_id = db.Column(db.Integer, db.ForeignKey('todos.id'))

    def __init__(self, title, todo_id, done=False, date_completed=None):
        self.title = title
        self.todo_id = todo_id
        self.done = done
        self.date_completed = date_completed

    def __repr__(self):
        return '<Task {}>'.format(self.title)



@app.route('/')
@app.route('/index')
def index():
    return redirect(url_for('todos_show'))


@app.route('/login', methods=['GET'])
def sessions_new():
    email = request.args.get('email')
    return render_template('login.html', email=email)


@app.route('/login', methods=['POST'])
def sessions_create():
    session.clear()
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email.lower()).first()
    if user and user.is_valid_password(password):
        session['email'] = user.email
        session['user_id'] = user.id
        return redirect(url_for('index'))
    else:
        flash("Email and password do not match!", 'error')
        return redirect(url_for('sessions_new', email=email))


@app.route('/logout', methods=['POST'])
def sessions_destroy():
    session.clear()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET'])
def accounts_new():
    email = request.args.get('email')
    return render_template('register.html', email=email)


@app.route('/register', methods=['POST'])
def accounts_create():
    email = request.form['email']
    password = request.form['password']
    password_confirm = request.form['password_confirm']
    if not email or not password or not password_confirm:
        flash("All fields should be filled!", 'error')
        return redirect(url_for('accounts_new', email=email))

    if password != password_confirm:
        flash("Passwords do not match!", 'error')
        return redirect(url_for('accounts_new', email=email))

    user = User(email, password)
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        app.logger.error(e)
        message = 'An account using {} is already registered!'.format(email)
        flash(message, 'error')
        return redirect(url_for('accounts_new'))

    flash('{} succesfully registered'.format(email))
    session.clear()
    session['email'] = user.email
    session['user_id'] = user.id
    return redirect(url_for('index'))


@app.route('/todos/', methods=['GET'])
def todos_show():
    todos = Todo.query.filter_by(private=False).all()
    return render_template('todos_show.html', todos=todos)


@app.route('/todos/new', methods=['GET'])
def todo_new():
    return render_template('todo_new.html')


@app.route('/todos/create', methods=['POST'])
def todo_create():
    return "Create todo"


@app.route('/todos/<todo_id>', methods=['GET'])
def todo_show(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if todo.user_id != session.get('user_id') and todo.private is True:
        abort(403)

    return render_template('todo_show.html', todo=todo)


@app.route('/todos/<todo_id>/edit', methods=['GET'])
def todo_edit(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if todo.user_id != session.get('user_id'):
        if todo.private is True:
            abort(403)
        else:
            return redirect(url_for('todo_show', todo_id=todo_id))

    return render_template('todo_edit.html', todo=todo)


@app.route('/todos/<todo_id>', methods=['POST'])
def todo_update(todo_id):
    return "Update todo"


@app.route('/tasks/create', methods=['POST'])
def task_create():
    return "Create task"



@app.before_request
def csrf_protect():
    if request.method == 'GET' and 'csrf_token' not in session:
        session['csrf_token'] = token_urlsafe()
        return None

    if request.method in ['POST', 'PUT', 'DELETE']:
        token = session.pop('csrf_token', None)
        if not token or token != request.form.get('csrf-token'):
            abort(403)


def token_urlsafe(num_bytes=16):
    """Return a random URL-safe text string, in Base64 encoding.

    Source: Python 3.6 secrets.token_urlsafe()
    https://github.com/python/cpython/blob/master/Lib/secrets.py

    """
    token = os.urandom(num_bytes)
    return base64.urlsafe_b64encode(token).rstrip(b'=').decode('ascii')


if __name__ == '__main__':
    app.run(debug=True)
