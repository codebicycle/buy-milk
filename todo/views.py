from secrets import token_urlsafe

from flask import (render_template, request, session, redirect, url_for,
                   flash, abort)
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, desc
from werkzeug.exceptions import HTTPException

from todo import app
from todo import db
from todo.forms import LoginForm, RegisterForm, TodoNewForm
from todo.models import User, Todo, Task
from todo.utils import https_only

PER_PAGE = app.config.get('PER_PAGE', 4)


@app.route('/')
@app.route('/index')
def index():
    session.pop('can_edit', None)
    return redirect(url_for('todos_show'))


@app.route('/login', methods=['GET'])
@https_only
def sessions_new():
    form = LoginForm()
    return render_template('login.html', form=form)


@app.route('/login', methods=['POST'])
@https_only
def sessions_create():
    clear_session()
    form = LoginForm(request.form)
    if form.validate_on_submit():
        session['email'] = form.user.email
        session['user_id'] = form.user.id
        return redirect(url_for('index'))

    return render_template('login.html', form=form)


@app.route('/logout', methods=['POST'])
def sessions_destroy():
    session.clear()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET'])
@https_only
def accounts_new():
    form = RegisterForm()
    return render_template('register.html', form=form)


@app.route('/register', methods=['POST'])
@https_only
def accounts_create():
    form = RegisterForm(request.form)
    if not form.validate_on_submit():
        return render_template('register.html', form=form)

    email = form.email.data.lower()
    user = User(email, form.password.data)
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        app.logger.error(e)
        message = 'An account using {} is already registered!'.format(email)
        flash(message, 'danger')
        return redirect(url_for('accounts_new'))

    session.clear()
    session['email'] = user.email
    session['user_id'] = user.id
    flash('{} succesfully registered'.format(email), 'success')
    return redirect(url_for('index'))


# Todos

@app.route('/todos/', methods=['GET'])
def todos_show():
    session.pop('can_edit', None)
    page = request.args.get('page', 1, type=int)

    todos = Todo.query.filter(Todo.private == False).order_by(desc(Todo.date_created))
    pagination = todos.paginate(page, PER_PAGE, False)

    return render_template('todos_show.html', todos=pagination)


@app.route('/my-todos')
def my_todos():
    page = (request.args.get('page', 1, type=int))

    if 'user_id' in session:
        user_todos = Todo.query.filter_by(user_id=session['user_id']
            ).order_by(desc(Todo.date_created))
    elif 'new_todos' in session and session['new_todos']:
        user_todos = Todo.query.filter(Todo.id.in_(session['new_todos'])
            ).order_by(desc(Todo.date_created))
    else:
        flash('You don\'t have any todos.', 'danger')
        return redirect(url_for('index'))

    pagination = user_todos.paginate(page, PER_PAGE, False)
    return render_template('todos_show.html', todos=pagination)


@app.route('/todos/new', methods=['GET'])
def todo_new():
    session.pop('can_edit', None)
    form = TodoNewForm()
    return render_template('todo_new.html', form=form)


@app.route('/todos/create', methods=['POST'])
def todo_create():
    session.pop('can_edit', None)
    form = TodoNewForm(request.form)
    if not form.validate_on_submit():
        return render_template('todo_new.html', form=form)

    user_id = session.get('user_id')

    title = request.form['title'].strip()
    todo = Todo(title, user_id)
    db.session.add(todo)
    db.session.commit()

    if user_id is None:
        if 'new_todos' not in session:
            session['new_todos'] = list()
        session['new_todos'].append(todo.id)
        session.modified = True

    task_title = form.task.data.strip()
    task = Task(task_title, todo.id)
    db.session.add(task)
    db.session.commit()

    return redirect(url_for('todo_edit', todo_id=todo.id))


@app.route('/todos/<int:todo_id>', methods=['GET'])
def todo_show(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if not is_editable_by_current_user(todo) and todo.private:
        abort(403)

    return render_template('todo_show.html', todo=todo)


@app.route('/todos/<int:todo_id>/edit', methods=['GET'])
def todo_edit(todo_id):
    session.pop('can_edit', None)
    todo = Todo.query.get_or_404(todo_id)

    if not is_editable_by_current_user(todo):
        return redirect(url_for('todo_show', todo_id=todo_id))

    form = TodoNewForm()
    return render_template('todo_edit.html', todo=todo, form=form)


def is_editable_by_current_user(todo):
    user_id = session.get('user_id')
    if user_id:
        return todo.user_id == user_id

    is_creator = False
    if 'new_todos' in session and session['new_todos']:
        is_creator = todo.id in session['new_todos']

    can_edit = False
    if 'can_edit' in session:
        can_edit =  todo.id == session['can_edit']

    return is_creator or can_edit


@app.route('/todos/<int:todo_id>', methods=['POST'])
def todo_update(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if not is_editable_by_current_user(todo):
        abort(403)

    todo.title = request.form['title'].strip()
    db.session.commit()
    session.pop('can_edit', None)
    return redirect_next(url_for('todo_edit', todo_id=todo.id))


@app.route('/todos/<int:todo_id>/delete', methods=['POST'])
def todo_destroy(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if not is_editable_by_current_user(todo):
        abort(403)

    if 'new_todos' in session and todo.id in session['new_todos']:
        session['new_todos'].remove(todo.id)
        session.modified = True

    db.session.delete(todo)
    db.session.commit()

    session.pop('can_edit', None)
    return redirect_next(url_for('todos_show'))


# Share URL

@app.route('/<url_token>', methods=['GET'])
@https_only
def shared_todo(url_token):
    todo = Todo.query.filter_by(url_token=url_token).first_or_404()
    session['can_edit'] = todo.id

    this_url = url_for('shared_todo', url_token=todo.url_token,
        _external=True)

    form = TodoNewForm()
    return render_template('todo_edit.html', todo=todo,
        next_url=this_url, form=form)


@app.route('/todos/<int:todo_id>/share', methods=["POST"])
@https_only
def url_create(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if not is_editable_by_current_user(todo):
        abort(403)

    if not todo.url_token:
        todo.url_token = token_urlsafe(16)
        db.session.commit()

    return redirect(url_for('url_show', todo_id=todo.id))


@app.route('/todos/<int:todo_id>/share', methods=['GET'])
@https_only
def url_show(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if not is_editable_by_current_user(todo):
        abort(403)

    if not todo.url_token:
        abort(404)

    shareable_url = url_for('shared_todo', url_token=todo.url_token,
    _external=True)
    back_url = url_for('todo_edit', todo_id=todo.id)

    return render_template('url_show.html', shareable_url=shareable_url,
        back_url=back_url)


# Tasks

@app.route('/tasks/create', methods=['POST'])
def task_create():
    todo_id = request.form['todo_id']
    todo = Todo.query.get_or_404(todo_id)
    if not is_editable_by_current_user(todo):
        abort(403)

    form = TodoNewForm(request.form)
    if not form.validate_on_submit():
        return render_template('todo_edit.html', todo=todo, form=form)

    task_title = request.form['task'].strip()
    task = Task(task_title, todo_id)
    db.session.add(task)
    db.session.commit()
    session.pop('can_edit', None)
    return redirect_next(url_for('todo_edit', todo_id=todo.id))


@app.route('/task/<int:task_id>/update', methods=['POST'])
def task_update(task_id):
    task = Task.query.get_or_404(task_id)
    if not is_editable_by_current_user(task.todo):
        abort(403)

    task.done = not task.done
    db.session.commit()
    session.pop('can_edit', None)
    return redirect_next(url_for('todo_edit', todo_id=task.todo_id))


@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
def task_destroy(task_id):
    task = Task.query.get_or_404(task_id)
    if not is_editable_by_current_user(task.todo):
        abort(403)

    db.session.delete(task)
    db.session.commit()
    session.pop('can_edit', None)
    return redirect_next(url_for('todo_edit', todo_id=task.todo_id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(400)
def bad_request(e):
    return render_template('400.html', error=e), 400


@app.errorhandler(403)
def forbiden(e):
    return render_template('403.html', error=e), 403


@app.errorhandler(HTTPException)
def http_error_handler(e):
    return render_template('error.html', error=e), e.code


def redirect_next(*args, **kwargs):
    next_url = request.form.get('next-url')
    if next_url:
        return redirect(next_url)

    return redirect(*args, **kwargs)


def clear_session():
    csrf_token = session.pop('csrf_token', None)
    session.clear()
    if csrf_token:
        session['csrf_token'] = csrf_token
