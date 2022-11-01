from flask import Flask, render_template, url_for, request, session, redirect,flash
import pymongo
import bcrypt
from functools import wraps
from flask_login import UserMixin,login_user,LoginManager,login_required,current_user,logout_user


app = Flask(__name__)
app.secret_key = 'mysecret'
client = pymongo.MongoClient("mongodb+srv://m001-student:arun-2002@cluster0.trsumto.mongodb.net/?retryWrites=true&w=majority")
db = client.login_users # database name = login_users

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(name):
    users = db.user_data
    data = users.find_one({'name':name})
    if data:
        return User(name=data['name'],password=data['password'])
    else:
        return None

class User(UserMixin):
    def __init__(self,name=None,password=None):
        self.name = name
        self.password = password

    def get_id(self):
        return self.name

# def not_logged(func):
#     @wraps(func)
#     def wrap(*args,**kwargs):
#         if 'name' not in session:
#             return func(*args,**kwargs)
#         else:
#             return redirect(url_for('index'))
#     return wrap


@app.route('/',methods=['POST','GET'])
@login_required
def index():
    return render_template('login.html')


@app.route('/login', methods=['POST','GET'])
#@not_logged
def login():
    if request.method == 'POST':
        users = db.user_data   # collection name = user_data
        name = request.form['name']
        password = request.form['password']
        Login_user = users.find_one({'name': name})  # find the name in database if name is present, it will store Login_user

        if Login_user: # bcrypt the usesr's password and compare allready stored password
            if bcrypt.hashpw(password.encode('utf-8'), Login_user['password']) == Login_user['password']:
                logged_user = User(Login_user['name'], Login_user['password'])
                login_user(logged_user)
                session['name'] = name  # using session to store the name
                return redirect(url_for("customer"))


        return 'Invalid username/password combination' # if the username and password is wrong it execute
    return render_template("login.html")

@app.route('/customer',methods=['POST','GET'])
@login_required
def customer():
    return render_template("customer.html")


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        users = db.user_data
        existing_user = users.find_one({'name': name})

        if existing_user is None:
            hashpass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            users.insert_one({'name': name, 'password': hashpass})
            #session['name'] = name
            return redirect(url_for('index'))

        return 'That username already exists!'

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('name',None)
    return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(debug=True,port=8000)


