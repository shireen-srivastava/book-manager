from flask import Flask, request, render_template, Response, json, redirect
from flask_pymongo import PyMongo
from flask_bcrypt import bcrypt

app = Flask(__name__)

app.config['MONGO_URI'] = "mongodb://localhost:27017/book_manager"
mongo = PyMongo(app)

#1 db with 2 collections
db = mongo.db.users
db1 = mongo.db.books

@app.route("/login", methods = ["GET"])
def homepage():
    new_user = []
    for i in db.find():
        new_user.append(i)
    return render_template("index.html", newuser = new_user)


@app.route("/registration", methods = ["POST", "GET"])
def createUsers():
    # password = request.json['password']
    # hash_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    # id = db.insert_one({
    #     'name': request.json['name'],
    #     'email' : request.json['email'],
    #     'password' : hash_password
    # })
    # print(id)
    # return "Registration Successfull"

    if request.method == "POST":

        new_name = request.form['name']
        new_email = request.form['email']
        password = request.form['password']
        hash_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        id = db.insert_one({
            'name':new_name,
            'email' : new_email,
            'password' : hash_password
        })

        return redirect("/registration")
    return render_template("register.html")
    


@app.route("/books", methods = ["POST"])
def createBooks():
    data = db1.insert_one({
        'name' : request.json['name'],
        'author' : request.json['author'],
        'description' : request.json['description'],
        'price' : request.json['price']
    })

    return Response(
        mimetype = "application/json",
        status = 201,
        response = json.dumps({"message" : "Book details added successfully", "id" : str(data.inserted_id)})
    )

@app.route("/books", methods = ["GET"])
def getbooks():
    new_book = []
    for i in db1.find():
        new_book.append(i)
    return render_template("book.html", newbook = new_book)

if __name__ == "__main__":
    app.run(debug=True)