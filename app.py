import sqlite3
from flask import Flask
from flask import render_template, request, redirect, g, session
from database import get_db, close_db, init_db
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "??????" #remember to swap

app.teardown_appcontext(close_db)

@app.route("/")
def index():
    db = get_db()
    recent_books = db.execute(
        "SELECT * FROM books ORDER BY id DESC LIMIT 5"
    ).fetchall()
    recent_reviews = db.execute(
        """SELECT reviews.*, books.title, users.username
            FROM reviews
            JOIN books ON reviews.book_id = books.id
            JOIN users ON reviews.user_id = users.id
            ORDER BY reviews.created_at DESC LIMIT 5"""
    ).fetchall()
    return render_template("index.html",
                           recent_books=recent_books,
                           recent_reviews=recent_reviews)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["Username"]
        password = request.form["Password"]
        confirm_password = request.form["Confimr_Password"]
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match")
        
        password_hash = generate_password_hash(password)
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    [username, password_hash])
            db.commit()
        except sqlite3.IntegrityError:
            return render_template("register.html", error="Username already taken")
        
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET" "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?",
                          [username]).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/")
        return render_template("login.html", error="Wrong username or password")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")