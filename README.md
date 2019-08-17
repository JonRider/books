# Project 1

Web Programming with Python and JavaScript

# Bookd Website

The Bookd website allows you to register for an account, sign in and then search for one of 5000 books. Possible matches will be displayed for a single search. The user may search by ISBN, book title or author.

# application.py

The main flask application file. This includes all the back-end logic for the website and all the routes.

# hash.py

This is a python file for hashing passwords which has two functions, hash_pass and verify_hash, which are imported and used by application.py. It uses the passlib library. The main function includes some test code.

# import.py

This file is used to import the books.csv file into the books table on the database.

# templates

The templates folder includes one base jinja layout template, layout.html. It also includes 4 other templates that extend layout: index.html, search.html, signup.html and book.html.

# static

The static folder includes the custom css stylesheet style.css.

# sql

The sql folder includes the sql commands for creating the three tables that are used in this project: book.sql, users.sql, reviews.sql for the sake of reference.

# books.csv

The original csv file that includes our books.

# requirements.txt

Includes a list of all the required python libraries.
