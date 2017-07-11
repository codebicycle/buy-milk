from flask import (render_template, request, session, redirect, url_for,
                   flash, abort)
from sqlalchemy.exc import IntegrityError

from todo import app
from todo import db
from todo.models import User, Todo, Task
from todo.utils import https_only, token_urlsafe


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
    user_todos = Todo.query.filter_by(user_id=session.get('user_id')).all()
    others_todos = Todo.query.filter(
        Todo.private == False,
        Todo.user_id != session.get('user_id')
    ).all()

    return render_template('todos_show.html', user_todos=user_todos,
                            others_todos=others_todos)


@app.route('/todos/new', methods=['GET'])
def todo_new():
    user_id = session.get('user_id')
    if not user_id:
        flash('Only logged-in users can create todo lists.')
        return redirect(url_for('sessions_new'))

    return render_template('todo_new.html')


@app.route('/todos/create', methods=['POST'])
def todo_create():
    user_id = session.get('user_id')
    if not user_id:
        abort(401)

    title = request.form['title']
    todo = Todo(title, user_id)
    db.session.add(todo)
    db.session.commit()
    return redirect(url_for('todo_edit', todo_id=todo.id))



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
    user_id = session.get('user_id')
    if not user_id:
        abort(401)

    # Check the todo edited is owned by the user
    todo = Todo.query.get_or_404(todo_id)
    if todo.user_id != user_id:
        abort(403)

    todo.title = request.form['title']
    db.session.commit()
    return redirect(url_for('todo_edit', todo_id=todo.id))


@app.route('/todos/<todo_id>/delete', methods=['POST'])
def todo_destroy(todo_id):
    user_id = session.get('user_id')
    if not user_id:
        abort(401)

    # Check the todo edited is owned by the user
    todo = Todo.query.get_or_404(todo_id)
    if todo.user_id != user_id:
        abort(403)

    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('todos_show'))


@app.route('/tasks/create', methods=['POST'])
def task_create():
    user_id = session.get('user_id')
    if not user_id:
        abort(401)

    todo_id = request.form['todo_id']

    # Check the todo edited is owned by the user
    todo = Todo.query.get_or_404(todo_id)
    if todo.user_id != user_id:
        abort(403)

    task = Task(request.form['task'], todo_id)
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('todo_edit', todo_id=todo.id))


@app.route('/task/<task_id>/update', methods=['POST'])
def task_update(task_id):
    user_id = session.get('user_id')
    if not user_id:
        abort(401)

    task = Task.query.get_or_404(task_id)
    if task.todo.user_id != user_id:
        abort(403)

    task.done = not task.done
    db.session.commit()

    return redirect(url_for('todo_edit', todo_id=task.todo_id))


@app.route('/tasks/<task_id>/delete', methods=['POST'])
def task_destroy(task_id):
    user_id = session.get('user_id')
    if not user_id:
        abort(401)

    task = Task.query.get_or_404(task_id)
    if task.todo.user_id != user_id:
        abort(403)

    db.session.delete(task)
    db.session.commit()

    return redirect(url_for('todo_edit', todo_id=task.todo_id))


@app.before_request
def csrf_protect():
    if request.method == 'GET' and 'csrf_token' not in session:
        session['csrf_token'] = token_urlsafe()
        return None

    if request.method in ['POST', 'PUT', 'DELETE']:
        token = session.pop('csrf_token', None)
        if not token or token != request.form.get('csrf-token'):
            abort(403)
