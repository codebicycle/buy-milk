from flask import (Flask, render_template, request, session, redirect, url_for,
                   flash)

from secrets import SECRET_KEY


app = Flask(__name__)
app.secret_key = SECRET_KEY


@app.route('/')
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')


@app.route('/login', methods=['GET'])
def sessions_new():
    email = request.args.get('email')
    return render_template('login.html', email=email)


@app.route('/login', methods=['POST'])
def sessions_create():
    session.clear()
    email = request.form['email']
    password = request.form['password']
    if valid_credentials(email, password):
        session['email'] = email
        return redirect(url_for('welcome'))
    else:
        flash("Email and password do not match!", 'error')
        return redirect(url_for('sessions_new', email=email))


@app.route('/logout', methods=['GET'])
def sessions_destroy():
    session.clear()
    return redirect(url_for('welcome'))


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

    if account_exists(email):
        message = 'An account using {} is already registered!'.format(email)
        flash(message, 'error')
        return redirect(url_for('accounts_new'))

    session.clear()
    session['email'] = email
    return redirect(url_for('welcome'))


CREDENTIALS = {
    'user@example.com': 'test',
    'test@example.com': 'test',
}

def account_exists(email):
    return email in CREDENTIALS

def valid_credentials(email, password):
    return email in CREDENTIALS and password == CREDENTIALS[email]


if __name__ == '__main__':
    app.run(debug=True)
