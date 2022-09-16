from flask import Flask, request, render_template, Response, json, redirect, flash, jsonify, session
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_session import Session
import re


app = Flask(__name__)

app.config['MONGO_URI'] = "mongodb://localhost:27017/book_manager"
app.config['SECRET_KEY'] = '234567iujhgvfcdsertyui98765427uywh'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

bcrypt = Bcrypt(app)
sessionv = Session(app)
mongo = PyMongo(app)

db = mongo.db.users
db1 = mongo.db.books

@app.route("/homepage", methods = ["GET"])
def homepage():
    return render_template("index.html")


@app.route("/registration", methods = ["GET","POST"])
def createUsers():
    if request.method == "POST":

        new_name = request.form['name']
        new_email = request.form['email']
        password = request.form['password']
        hash_password = bcrypt.generate_password_hash(password)
        
        if not re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', new_email):
            flash(f"Email not satisfied")

        elif list(db.find({"email":new_email})):
            flash(f"Email already in use!! Try with different email")
        
        elif not re.fullmatch(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,10}$', password):
            flash(f"Password should contain 8-10 characters with atleast 1 uppercase letter, lowercase letter, digit, and a special character")

        else:
            id = db.insert_one({
                'name':new_name,
                'email' : new_email,
                'password' : hash_password
            })
            flash(f"Account created for {new_name} successfully")
            return redirect("/login")
    return render_template("register.html")
    

@app.route("/login", methods = ["GET", "POST"])
def getuser():
    global userid
    if request.method == "POST":
        new_email = request.form['email']
        password = request.form['password']

        res = db.find({"email": new_email},{"_id":1,"password":1})
        l = list(res)

        if len(l) != 0 and bcrypt.check_password_hash(l[0]["password"],password):
            session["email"] = new_email
            userid = l[0]["_id"]
            flash(f"You are successfully logged in!",'success') 
            return redirect("/books")
        else:
            flash(f"Invalid Email ID or Password",'danger')
            return redirect("/login")
    return render_template("login.html")


@app.route("/books", methods = ["GET"])
def getbooks():
    if session["email"]:
        print(session['email'])
        new_book = []
        data = db1.find({"userid": userid})
        for i in data:
            new_book.append(i)
        print(new_book)
        return render_template("book.html", newbook = new_book)
    else:
        return redirect("/login")


@app.route("/readbooks", methods = ["GET"])
def getreadbooks():
    if session["email"]:
        print(session['email'])
        new_book = []
        data = db1.find({"userid": userid, "read":"true"})
        for i in data:
            new_book.append(i)
        print(new_book)
        return render_template("readbooks.html", newbook = new_book)
    else:
        return redirect("/login")


@app.route("/users", methods = ["GET"])
def getprofile():
    user = []
    for i in db.find({"email" : session["email"]}):
        user.append(i)
    return render_template("userdetails.html", user = user)


@app.route("/addbook", methods = ["GET", "POST"])
def createBooks():
    if session["email"]:
        if request.method == "POST":
            name = request.form['name']
            author = request.form['author']
            description = request.form['description']
            price = request.form['price']
            read = request.form['read']

            id = db1.insert_one({
                'userid': userid,
                'name': name,
                'author' : author,
                'description' : description,
                'price' : price,
                'read' : read
            })
            flash(f"Book added successfully",'success')
            return redirect("/books")
        return render_template("addbook.html")  
    else:
        return redirect("/login")


@app.route("/books/<bookid>", methods = ["GET"])
def getbook(bookid):
    if session["email"]:
        new_book = []
        for i in db1.find({"_id" : ObjectId(bookid)}):
            new_book.append(i)
        return render_template("bookdetails.html", newbook = new_book)
    else:
        return redirect("/login")


@app.route('/deletebooks/<bookid>', methods=["GET", "POST"])
def delete_book(bookid):
    if session["email"]:
        db1.delete_one({"_id":ObjectId(bookid)})
        flash(f"Book deleted successfully!!",'success')
        return redirect("/books")
    else:
        return redirect("/login")


@app.route('/updatebooks/<bookid>', methods=["GET", "POST"])
def update_book(bookid):
    if session["email"]:
        if request.method == "GET":
            book = []
            for i in db1.find({"_id" : ObjectId(bookid)}):
                book.append(i)
                
        if request.method == "POST":
            name = request.form['name']
            author = request.form['author']
            description = request.form['description']
            price = request.form['price']
            read = request.form['read']
            db1.update_one({"_id":ObjectId(bookid)}, {'$set' : {"name":name, "author":author, "description":description, "price":price, "read":read}})
                
            flash(f"Book updated successfully!!",'success')
            return redirect("/books")
        return render_template("updatebook.html", book = book)
    else:
        return redirect("/login")


@app.route("/logout")
def logout():
    session["email"] = None
    return redirect("/homepage")


app.run(debug=True)

if __name__ == "__main__":
    app.run(debug=True)