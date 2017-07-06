from flask import (Flask, render_template, request, session, redirect, url_for,
                   flash)



app = Flask(__name__)
app.secret_key = b'T\xa3\x92\r]\xea\x9db\x99s-\x17m\x8a\xe0\xd8\xf82*\xc4\x07\x12\xe3\x14'

@app.route('/')
@app.route('/welcome')
def welcome():
    email = session.get('email')
    if not email:
        return redirect(url_for('sessions_new'))
    return render_template('welcome.html', title='Welcome', email=email)


@app.route('/login', methods=['GET'])
def sessions_new():
    return render_template('login_form.html')


@app.route('/login', methods=['POST'])
def sessions_create():
    email = request.form.get('email')
    password = request.form.get('password')
    if are_valid_credentials(email, password):
        session['email'] = email
        return redirect( url_for('welcome'))
    else:
        flash("Email and password do not match!", 'error')
        return redirect( url_for('sessions_new'))


def are_valid_credentials(email, password):
    credentials = {
        'user@example.com': 'test',
    }
    return email in credentials and password == credentials[email]


if __name__ == '__main__':
    app.run(debug=True)
