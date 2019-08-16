import os
import requests

from flask import Flask, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Check for Goodpreads API KEy
if not os.getenv("GOOD_KEY"):
    raise RuntimeError("GOOD_KEY is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Set Goodreads API KEy
key = os.getenv("GOOD_KEY")

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
                # Log the user into the session
                session["username"] = username
                session["user_id"] = user.id
                return render_template("search.html", username=session["username"])
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
            # Check to see what the user_id was set up as in the database
            user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
            # Log user into the session
            session["username"] = username
            session["user_id"] = user.id
            return render_template("search.html", username=session["username"])

    return render_template("signup.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    """Allow users to search for books."""

    # Make sure user is logged in
    if "username" not in session:
        return render_template("index.html", message="Please login to view that page!")

    if request.method == "POST":
        # Get search form
        search = request.form.get("search").strip()
        search_partial = search + '%'

        books = db.execute("SELECT * FROM books WHERE isbn LIKE :search OR author LIKE :search OR title LIKE :search", {"search": search_partial}).fetchall()

        return render_template("search.html", username=session["username"], search=search, books=books)

    # If travelling from GET
    return render_template("search.html", username=session["username"])

@app.route("/book/<title>", methods=["GET", "POST"])
def book(title):
    """Detail page for individual book."""

    # Make sure user is logged in
    if "username" not in session:
        return render_template("index.html", message="Please login to view that page!")

    # Retrieve book row from database
    book = db.execute("SELECT * FROM books WHERE title = :title", {"title": title}).fetchone()

    # Make sure it exists if someone types in a random route
    if book is None:
        return render_template("search.html", search=title)

    # Get average rating and number of ratings from Goodreads
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": book.isbn})
    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")
    data = res.json()
    average_rating = data["books"][0]["average_rating"]
    ratings_count = data["books"][0]["ratings_count"]

    # Setup default message
    message = "Write your review here"

    if request.method == "POST":
        # Get rating and review
        rating = int(request.form.get("rating"))
        review = request.form.get("review")

        # Check if user hasn't yet left a review for this book
        if db.execute("SELECT * FROM reviews JOIN books ON reviews.books_id = books.id WHERE user_id = :user_id AND books_id = :books_id", {"user_id": session["user_id"], "books_id": book.id}).rowcount == 0:

            # Add rating to review table with user_id and book_id
            db.execute("INSERT INTO reviews (rating, review, books_id, user_id) VALUES (:rating, :review, :books_id, :user_id)",
                    {"rating": rating, "review": review, "books_id": book.id, "user_id": session["user_id"]})
            db.commit()
        else:
            message = "You have already left a review for that title!"

        # Get updated reviews
        reviews = db.execute("SELECT rating, review, username FROM reviews JOIN users ON reviews.user_id = users.id WHERE books_id = :books_id", {"books_id": book.id}).fetchall()

        return render_template("book.html", message=message, reviews=reviews, username=session["username"], book=book, average_rating=average_rating, ratings_count=ratings_count)

    # Get ratings and reviews from database if in GET method
    reviews = db.execute("SELECT rating, review, username FROM reviews JOIN users ON reviews.user_id = users.id WHERE books_id = :books_id", {"books_id": book.id}).fetchall()

    return render_template("book.html", message=message, reviews=reviews, username=session["username"], book=book, average_rating=average_rating, ratings_count=ratings_count)

@app.route("/api/<int:isbn>")
def api(isbn):
    """Get API request."""
    return render_template("index.html")

@app.route("/logout")
def logout():
    """Logout Session"""
    # If not logged in return to index
    if "username" not in session:
        return render_template("index.html")

    # Log the user out of the session
    session.pop("username")
    session.pop("user_id")
    return render_template("index.html")
