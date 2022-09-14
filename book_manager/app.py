from flask import Flask, request, render_template, Response, json, redirect, flash, jsonify
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from bson.objectid import ObjectId


app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['MONGO_URI'] = "mongodb://localhost:27017/book_manager"
app.config['SECRET_KEY'] = 'shireensrivastava1234'
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
            userid = l[0]["_id"]
            flash(f"You are successfully logged in!",'success') 
            return redirect("/books")
        else:
            flash(f"Invalid Email ID or Password",'danger')
            return redirect("/login")
    return render_template("login.html")


@app.route("/logout")
def logout():
    return redirect("/homepage")


@app.route("/addbook", methods = ["GET", "POST"])
def createBooks():
    if request.method == "POST":

        name = request.form['name']
        author = request.form['author']
        description = request.form['description']
        price = request.form['price']

        id = db1.insert_one({
            'userid': userid,
            'name': name,
            'author' : author,
            'description' : description,
            'price' : price
        })
        flash(f"Book added successfully",'success')
        return redirect("/books")
    return render_template("addbook.html")


@app.route("/books", methods = ["GET"])
def getbooks():
    new_book = []
    for i in db1.find({"userid": userid}):
        new_book.append(i)
    return render_template("book.html", newbook = new_book)


@app.route("/books/<bookid>", methods = ["GET"])
def getbook(bookid):
    new_book = []
    for i in db1.find({"_id" : ObjectId(bookid)}):
        new_book.append(i)
    return render_template("bookdetails.html", newbook = new_book)


@app.route('/deletebooks/<bookid>', methods=["GET", "POST"])
def delete_book(bookid):
    db1.delete_one({"_id":ObjectId(bookid)})
    flash(f"Book deleted successfully!!",'success')
    return redirect("/books")

app.run(debug=True)

if __name__ == "__main__":
    app.run(debug=True)