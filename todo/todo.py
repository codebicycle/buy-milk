from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
@app.route('/welcome')
def welcome():
    return render_template('welcome.html', title='Welcome')


@app.route('/login', methods=['GET'])
def sessions_new():
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
