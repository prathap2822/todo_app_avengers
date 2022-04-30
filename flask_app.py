from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from secretkey import key
from werkzeug.security import generate_password_hash, check_password_hash




app = Flask(__name__)
app.secret_key = key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    """User account model."""

    __tablename__ = 'flasklogin-users'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    name = db.Column(
        db.String(100),
        nullable=False,
        unique=False
    )
    email = db.Column(
        db.String(40),
        unique=True,
        nullable=False
    )
    password = db.Column(
        db.String(200),
        primary_key=False,
        unique=False,
        nullable=False
	)

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(
            password,
            method='sha256'
        )

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.name)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signUpUser', methods=['GET'])
def signUpUser():
    return render_template('signup.html')

@app.route('/signup', methods=['POST','GET'])
def signUp():
    user = User(name = request.form['username'], email = request.form['email'])
    exists = db.session.query(db.exists().where(User.email == request.form['email'])).scalar()
    if(exists):
        session['username'] = request.form['username']
        return render_template('login.html', exists = exists)
    user.set_password(request.form['user_password'])
    db.session.add(user)
    db.session.commit()
    print("done")
    return render_template('index.html')

@app.route('/loginUser', methods=['GET','POST'])
def loginUser():
    return render_template('login.html')

@app.route('/login', methods=['GET','POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    exists = db.session.query(db.exists().where(User.email == email)).scalar()
    if(exists):
        conn = db.engine.connect()
        curr = conn.execute("SELECT password FROM 'flasklogin-users' WHERE email='{e}'".format(e=email))
        passHash = curr.fetchone()[0]
        if(check_password_hash(passHash,password)):
            curr = conn.execute("SELECT name FROM 'flasklogin-users' WHERE email='{e}'".format(e=email))
            username = curr.fetchone()[0]
            session['username'] = username
            return render_template('welcome.html', exists = exists, session = session)
        return render_template('welcome.html', exists = exists)
    return render_template('index.html')

if __name__ == '__main__':
    app.run()