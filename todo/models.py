from datetime import datetime

import bcrypt

from todo import db


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
    tasks = db.relationship('Task', backref='todo', lazy='select',
        order_by='Task.id')


    def __init__(self, title, user_id=None, private=False):
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
