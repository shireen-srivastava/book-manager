from flask import Flask, request, render_template, Response, json, redirect, flash, jsonify, session
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_session import Session
from flask_paginate import Pagination, get_page_parameter
import re
import os
import pathlib
import requests

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


# Returns index page which shows login/signup.
@app.route("/homepage", methods = ["GET"])
def homepage():
    return render_template("index.html")


# User's Registration route.
# Takes input name, email, password.
@app.route("/registration", methods = ["GET","POST"])
def createUsers():
    if request.method == "POST":

        new_name = request.form['name']
        new_email = request.form['email']
        password = request.form['password']

        # Password Encryption
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
    

# User's Login route.
# Takes input email, password.
# Returns user dashboard.
@app.route("/login", methods = ["GET", "POST"])
def getuser():
    global userid
    if request.method == "POST":
        new_email = request.form['email']
        password = request.form['password']

        # Finds password through email entered by user.
        res = db.find({"email": new_email},{"_id":1,"password":1})
        l = list(res)
        
        # If email exists, checks if hashed password matches with the password entered by user.
        if len(l) != 0 and bcrypt.check_password_hash(l[0]["password"],password):

            # Creating session for logged in user.
            session["email"] = new_email

            # Storing _id of logged in user.
            userid = l[0]["_id"]
            flash(f"You are successfully logged in!",'success') 
            return redirect("/books")
        else:
            flash(f"Invalid Email ID or Password",'danger')
            return redirect("/login")
    return render_template("login.html")


# User can reset their password.
# Takes input email, current password and new password.
@app.route("/forgotpassword", methods=["GET", "POST"])
def forgotpassword():
    if request.method == "POST":
        email = request.form['email']
        oldpassword = request.form['oldpassword']
        newpassword = request.form['newpassword']

        # Encrypted new password.
        newhashpassword = bcrypt.generate_password_hash(newpassword)

        # Finds current password through email entered by user.
        res = db.find({"email": email},{"_id":1,"password":1})
        l = list(res)

        # Checks if current password matches.
        if len(l) != 0 and bcrypt.check_password_hash(l[0]["password"],oldpassword):
            if not re.fullmatch(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,10}$', newpassword):
                flash(f"Password should contain 8-10 characters with atleast 1 uppercase letter, lowercase letter, digit, and a special character")
            else:

                # Update new encrypted password.
                db.update_one({"email":email}, {'$set' : {"password" : newhashpassword}})
                flash(f"Password updated for {email} successfully!!")
                return redirect("/login")
        else:
            flash(f"Email ID or Current Password incorrect")
            return redirect("/forgotpassword")
    return render_template("forgotpassword.html")


# To fetch all the books for logged in user.
# Takes @parameter userid of logged in user.
@app.route("/books", methods = ["GET"])
def getbooks():
    if session["email"]:
        new_book = []
        data = db1.find({"userid": userid})
        for i in data:
            new_book.append(i)
        return render_template("book.html", newbook = new_book)
    else:
        return redirect("/login")


# To fetch particular book with details.
# Takes @parameter _id of particular book.
@app.route("/books/<bookid>", methods = ["GET"])
def getbook(bookid):
    if session["email"]:
        new_book = []
        for i in db1.find({"_id" : ObjectId(bookid)}):
            new_book.append(i)
        return render_template("bookdetails.html", newbook = new_book)
    else:
        return redirect("/login")


# To fetch all the books read by particular user. 
# Checks when read = true.
@app.route("/readbooks", methods = ["GET"])
def getreadbooks():
    if session["email"]:
        print(session['email'])
        new_book = []
        data = db1.find({"userid": userid, "read":True})
        for i in data:
            new_book.append(i)
        return render_template("readbooks.html", newbook = new_book)
    else:
        return redirect("/login")


# To create a book for user.
# Returns name, author, genres, price of book.
@app.route("/addbook", methods = ["GET", "POST"])
def createBooks():
    if session["email"]:
        if request.method == "POST":
            name = request.form['name']
            author = request.form['author']
            genres = request.form['genres']
            price = request.form['price']

            id = db1.insert_one({
                'userid': userid,
                'name': name,
                'author' : author,
                'genres' : genres,
                'price' : price,
                'read' : False
            })
            flash(f"Book added successfully",'success')
            return redirect("/books")
        return render_template("addbook.html")  
    else:
        return redirect("/login")


# To delete the book from database.
@app.route('/deletebooks/<bookid>', methods=["GET", "POST"])
def delete_book(bookid):
    if session["email"]:
        db1.delete_one({"_id":ObjectId(bookid)})
        flash(f"Book deleted successfully!!",'success')
        return redirect("/books")
    else:
        return redirect("/login")


# GET : To fetch the current book details.
# POST : To update the book details. 
# Takes @parameters name, author, genres, price, read of book.
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
            genres = request.form['genres']
            price = request.form['price']
            if request.form['read'] == "true":
                read = True
            else:
                read = False
            db1.update_one({"_id":ObjectId(bookid)}, {'$set' : {"name":name, "author":author, "genres":genres, "price":price, "read":read}})
                
            flash(f"Book updated successfully!!",'success')
            return redirect("/books")
        return render_template("updatebook.html", book = book)
    else:
        return redirect("/login")


# To fetch all the unsubscribed books.
# Check when userid is null.
genres=""
bookname=""
@app.route("/subscribebooks", methods = ["GET","POST"])
def subscribebooks():
    global genres
    global bookname
    if session["email"]:
        PER_PAGE = 8
        new_book = []
        if genres:
            data = db1.find({"userid": "",'genres':genres})
            genres=None

        elif bookname:
            data = db1.find({"userid": "", 'name':bookname})
            bookname=None

        else:
            data = db1.find({"userid": ""})
         
        page = request.args.get(get_page_parameter(), type=int, default=1)
        for j in data:
            new_book.append(j)
        i=(page-1)*PER_PAGE
        bbooks = new_book[i:i+8]
        pagination = Pagination(page=page, total=len(new_book),per_page=PER_PAGE, record_name='books', css_framework='bootstrap4')

        return render_template("subscribe.html",new_book=bbooks,pagination=pagination)
    else:
        return redirect("/login")


# To subscribe a particular book.
# Updates userid of particular book with the logged in userid.
@app.route("/subscribebutton/<bookid>", methods = ["GET","POST"])
def subscribebutton(bookid):
    if session["email"]:
        db1.update_one({"_id":ObjectId(bookid)}, {'$set' : {"userid":userid}})
        flash("You have successfully subscribed the book!!")
        return redirect("/subscribebooks")
    else:
        return redirect("/login")


# To unsubscribe a particular book.
# Updates userid of subscribed book with null.
# Also update, read = False when unsubscribing a book.
@app.route("/unsubscribebutton/<bookid>", methods = ["GET","POST"])
def unsubscribebutton(bookid):
    if session["email"]:
        db1.update_one({"_id":ObjectId(bookid)}, {'$set' : {"userid":"", "read" : False}})
        flash("You have successfully unsubscribed the book!!")
        return redirect("/subscribebooks")
    else:
        return redirect("/login")


# To recommend books according to genres, user subscribed.
# Returns 3 books of each genres.
@app.route("/recommend", methods = ["GET","POST"])
def recommend():
    if session["email"]:
        kl=[]
        # To find all the genres user subscribed.
        data = db1.find({"userid":userid},{"genres":1,"_id":0})
        usergenres = list(data)

        # To remove duplicate genres.
        setgenres = set(d.get('genres', 'alt') for d in usergenres)
    
        # To find the book which are unsubscribed, of same genres user subscribed.
        for i in setgenres:
            kl.append(list(db1.find({"userid": "", "genres" : i}).limit(3)))
        return render_template("recommend.html", kl = kl)
    else:
        return redirect("/login")


# To fetch user details with session.
@app.route("/users", methods = ["GET"])
def getprofile():
    user = []
    for i in db.find({"email" : session["email"]}):
        user.append(i)
    return render_template("userdetails.html", user = user)


# Filtering books based on genre
@app.route("/filterSubscribeBooks/<genre>", methods = ["GET"])
def getGenres(genre):
    global genres
    genres=genre
    return redirect("/subscribebooks")


@app.route("/searchbar", methods = ["GET", "POST"])
def searchbar():
    global bookname
    if request.method == "POST":
        bookname = request.form["bookname"]
    return redirect("/subscribebooks")


# Logout from session.
@app.route("/logout")
def logout():
    session["email"] = None
    return redirect("/homepage")


app.run(debug=True)

if __name__ == "__main__":
    app.run(debug=True)