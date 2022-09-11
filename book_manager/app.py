from flask import Flask, request, render_template, Response, json, redirect, flash
from flask_pymongo import PyMongo
from flask_bcrypt import bcrypt

app = Flask(__name__)

app.config['MONGO_URI'] = "mongodb://localhost:27017/book_manager"
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
        id = db.insert_one({
            'name':new_name,
            'email' : new_email,
            'password' : password
        })

        return redirect("/login")
    return render_template("register.html")
    

@app.route("/login", methods = ["GET", "POST"])
def getuser():
    if request.method == "POST":
        new_email = request.form['email']
        password = request.form['password']

        res = db.find({"email": new_email, "password": password})
        if len(list(res)) != 0:
            return redirect("/books")
        else:
            print("Incorrect email id or password")
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
            'name': name,
            'author' : author,
            'description' : description,
            'price' : price
        })

        return redirect("/books")
    return render_template("addbook.html")


@app.route("/books", methods = ["GET"])
def getbooks():
    new_book = []
    for i in db1.find():
        new_book.append(i)
    return render_template("book.html", newbook = new_book)


if __name__ == "__main__":
    app.run(debug=True)