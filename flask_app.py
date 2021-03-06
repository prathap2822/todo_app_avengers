from datetime import datetime
import email
from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from secretkey import key
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from email_user import Mailer


log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


logging.basicConfig(filename=r'.\logs\user.log', encoding='utf-8', level=logging.DEBUG)
app = Flask(__name__)
app.secret_key = key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

mailer = Mailer()

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
        unique=True
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

class Todo(db.Model):
    __tablename__ = 'todoitems'
    todo_id = db.Column(
        db.Integer,
        primary_key=True
    )
    username = db.Column(
        db.String(40),
        nullable=False
    )
    title = db.Column(
        db.String(40),
        nullable=False
    )
    description = db.Column(
        db.String(100),
        nullable=False
    )
    due_date = db.Column(
        db.Date(),
        nullable=False
    )
    created_date = db.Column(
        db.Date(),
        nullable=False
    )
    def __init__(self, username: str) -> None:
        self.username = username
        self.created_date = datetime.now()
        __tablename__ = 'todoitems'
        super().__init__()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signUpUser', methods=['GET'])
def signUpUser():
    return render_template('signup.html')

@app.route('/signup', methods=['POST','GET'])
def signUp():
    user = User(name = request.form['username'], email = request.form['email'])
    exists = db.session.query(db.exists().where(User.email == request.form['email'])).scalar() or db.session.query(db.exists().where(User.name == request.form['username'])).scalar()
    if(exists):
        session['username'] = request.form['username']
        return render_template('login.html', exists = exists)
    user.set_password(request.form['user_password'])
    db.session.add(user)
    db.session.commit()
    try:
        mailer.message(subject="Avengers To-do Application", text="""Hello {},\n\nThank you for registering with Avengers To-Do application. \nVisit http://avengers2.pythonanywhere.com/ to manage your To-Do list.\n\nRegards,\nAvengers Team""".format(request.form['username']))
        mailer.send(to=[request.form['email']])
        mailer.close()
    except:
        pass
    logging.info(msg="{} signed up at {}".format(request.form['username'], datetime.now()))
    return render_template('index.html')

@app.route('/loginUser', methods=['GET','POST'])
def loginUser():
    return render_template('login.html')

@app.route('/login', methods=['GET','POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    exists = db.session.query(db.exists().where(User.name == username)).scalar()
    if(exists):
        conn = db.engine.connect()
        curr = conn.execute("SELECT password FROM 'flasklogin-users' WHERE name='{e}'".format(e=username))
        passHash = curr.fetchone()[0]
        if(check_password_hash(passHash,password)):
            curr = conn.execute("SELECT name FROM 'flasklogin-users' WHERE name='{e}'".format(e=username))
            username = curr.fetchone()[0]
            session['username'] = username
            session['active'] = True
            logging.info(msg="{} logged in at {}".format(username, datetime.now()))
            curr = conn.execute("SELECT * FROM 'todoitems' WHERE username ='{}'".format(username))
            todos = curr.fetchall()
            return render_template('welcome.html', exists = exists, session = session, todos= todos)
        return render_template('login.html', exists = exists, session = {'error': 'Incorrect Password or email'})
    return render_template('login.html', session = {'error': 'Incorrect Password or email'})

@app.route('/addTodo/<username>', methods = ['POST'])
def addTodo(username):
    todo = Todo(username=username)
    todo.title = request.form['todo_title']
    todo.description = request.form['todo_description']
    todo.username = username
    date = request.form['duedate']
    todo.due_date = datetime(year=int(date[0:4]), month=int(date[5:7]), day=int(date[8:10]))
    db.session.add(todo)
    db.session.commit()
    session['username'] = username


    conn = db.engine.connect()
    curr = conn.execute("SELECT email FROM 'flasklogin-users' where name='{}'".format(username))
    email = curr.fetchone()[0]

    e = db.engine
    with e.connect() as conn:
        curr = conn.execute("SELECT * FROM 'todoitems' WHERE username ='{}'".format(username))
        todos = curr.fetchall()
    return render_template('welcome.html',session = session, todos = todos)

@app.route('/deleteTodo/<username>/<id>', methods = ['POST', 'GET'])
def deleteTodo(username, id):
    e = db.engine
    with e.connect() as conn:
        curr = conn.execute("DELETE FROM 'todoitems' WHERE username ='{}' and todo_id = '{}';".format(username, id))
        db.session.commit()
        curr = conn.execute("SELECT * FROM 'todoitems' WHERE username ='{}'".format(username))
        todos = curr.fetchall()
    return render_template('welcome.html',session = session, todos = todos)

@app.route('/calendarView/<username>')
def calendarView(username):
    data = {}
    with db.engine.connect() as conn:
        curr = conn.execute("SELECT * FROM 'todoitems' WHERE username='{}' ORDER BY due_date".format(username))
        data = curr.fetchall()
    return render_template('calendar.html', data = data, username=username)

@app.route('/welcome/<username>')
def welcome(username):
    session = {}
    session['username'] = username
    return render_template('welcome.html', session=session)

@app.route('/logout')
def logout():
    return render_template('index.html')



if __name__ == '__main__':
    app.run()