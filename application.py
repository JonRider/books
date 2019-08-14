import os

from flask import Flask, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get username and password
        username = request.form.get("username")
        password = request.form.get("password")

        # Check for blank password
        if password == '':
            return render_template("index.html", message="Password cannot be blank!")

        # Check for blank username
        if username == '':
            return render_template("index.html", message="Username cannot be blank!")

        # Check if usename does not exist
        if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 0:
            return render_template("index.html", message="Username doesn't exist!")

        # Check if password is correct then login
        else:
            user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
            if user.password == password:
                return render_template("search.html", username=username)
            else:
                return render_template("index.html", message="Invalid Password!")


    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Get username and password
        username = request.form.get("username")
        password = request.form.get("password")

        # Check for blank password
        if password == '':
            return render_template("signup.html", message="Password cannot be blank!")

        # Check for blank username
        if username == '':
            return render_template("signup.html", message="Username cannot be blank!")

        # Check if usename does not exist
        if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 1:
            return render_template("signup.html", message="Username already exists!")
        # Otherwise add it to the database
        else:
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                    {"username": username, "password": password})
            db.commit()
            return render_template("search.html", username=username)

    return render_template("signup.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    """Allow users to search for books."""
    if request.method == "POST":
        # Get search form
        search = request.form.get("search").strip()
        search_partial = search + '%'

        books = db.execute("SELECT * FROM books WHERE isbn LIKE :search OR author LIKE :search OR title LIKE :search", {"search": search_partial}).fetchall()

        return render_template("search.html", search=search, books=books)
    #actually you cant get this without being logged in
    return render_template("search.html")

@app.route("/book/<title>")
def book(title):
    """Detail page for individual book."""
    return render_template("book.html", title=title)

@app.route("/api/<int:isbn>")
def api(isbn):
    """Get API request."""
