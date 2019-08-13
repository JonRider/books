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


        # Check if usename does not exist
        if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 0:
            return render_template("index.html", message="Username doesn't exist!")

        # Check if password is correct then login
        else:
            user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
            if user.password == password:
                return render_template("books.html")
            else:
                return render_template("index.html", message="Invalid Password!")


    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Get username and password
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if usename does not exist
        if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 1:
            return render_template("signup.html", message="Username already exists!")
        # Otherwise add it to the database
        else:
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                    {"username": username, "password": password})
            db.commit()
            return render_template("books.html", username=username, password=password)

    return render_template("signup.html")
