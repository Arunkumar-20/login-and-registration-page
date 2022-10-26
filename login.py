from flask import Flask, render_template, url_for, request, session, redirect
import pymongo
import bcrypt

app = Flask(__name__)
client = pymongo.MongoClient("mongodb+srv://m001-student:arun-2002@cluster0.trsumto.mongodb.net/?retryWrites=true&w=majority")
db = client.login_users # database name = login_users

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    users = db.user_data   # collection name = user_data
    name = request.form['name']
    password = request.form['password']
    Login_user = users.find_one({'name': name})  # find the name in database if name is present, it will store Login_user

    if Login_user: # bcrypt the usesr's password and compare allready stored password
        if bcrypt.hashpw(password.encode('utf-8'), Login_user['password']) == Login_user['password']:
            session['name'] = name  # using session to store the name
            return redirect(url_for('customer'))

    return 'Invalid username/password combination' # if the username and password is wrong it execute


@app.route('/customer',methods=['POST','GET'])
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
            session['name'] = name
            return redirect(url_for('index'))

        return 'That username already exists!'

    return render_template('register.html')


if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True)
