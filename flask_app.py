from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user
from secretkey import key
login_manager = LoginManager()


app = Flask(__name__)
app.secret_key = key
login_manager.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)


class user(db.Model):
    id = db.Column('user_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(50))
    passhash = db.Column(db.String(50))
    def is_authenticated():
        return False
    def is_active():
        return True
    def is_anonymous():
        return True
    def get_id():
        return str(id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST', 'GET'])
def login():
    return render_template("signup.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    #TODO: Create a User Object
    login_user(user)

    flash('Logged in successfully.')
    form = None
    return render_template('login.html', form=form)

@app.route('/signUpUser', methods=['POST', 'GET'])
def signUpUser():
    print(request.form['username'], )
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)