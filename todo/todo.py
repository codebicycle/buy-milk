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
    return render_template('login_form.html', email=email)


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


def valid_credentials(email, password):
    credentials = {
        'user@example.com': 'test',
    }
    return email in credentials and password == credentials[email]


if __name__ == '__main__':
    app.run(debug=True)
