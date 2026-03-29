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

@app.route("/books")
def books():
    db = get_db()
    query = request.args.get("query", "")

    if query:
        results = db.execute(
            """SELECT * FROM books
                WHERE LOWER(title) LIKE LOWER(?)
                OR LOWER(author) LIKE LOWER(?)""",
            [f"%{query}", f"%{query}"]
        ).fetchall()
    else:
        results = db.execute("SELECT * FROM books").fetchall()

    return render_template("books.html", books=results, query=query)

@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if not session.get("user.id"):
        return redirect("/login")
    
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        year = request.form["year"] or None
        db = get_db()
        db.execute(
            "INSERT INTO books (title, author, year, created_by) VALUES (?, ?, ?, ?)",
            [title, author, year, session["user_id"]]
        )
        db = get_db()
        book = db.execute(
            "SELECT *FROM books WHERE title = ? AND created_by = ? ORDER BY id DESC LIMIT 1",
            [title, session["user_id"]]
        ).fetchone()
        return redirect(f"/books/{book['id']}")
    
    query = request.args.get("query", "")
    return render_template("add_book.html", query=query)

@app.route("/book/<int:book_id>")
def book(book_id):
    db = get_db()
    book = db.execute(
        "SELECT * FROM books WHERE id = ?", [book_id]
    ).fetchone()

    if not book:
        return redirect("/books")
    
    reviews = db.execute(
        """SELECT reviews.*, users.username
            FROM reviews
            JOIN users ON reviews.user_id = user.id
            WHERE reviews.book_id = ?
            ORDER BY reviews.created_at DESC""",
        [book_id]
    ).fetchall()

    avg_rating = db.execute(
        "SELECT ROUND(AVG(rating), 1) as avg FROM reviews WHERE book_id = ?",
        [book_id]
    ).fetchone()["avg"]

    comments = db.execute(
        """SELECT comments.*m users.username
            FROM comments
            JOIN users ON comments.user_id = users.id
            WHERE comments.review_ID IN(
                SELECT id FROM reviews WHERE book_id = ?
            )
            ORDER BY comments.created at ASC""",
            [book_id]
    ).fetchall()

    user_review = None
    if session.get("user_id"):
        user_review = db.execute(
            "SELECT * FROM reviews WHERE user_id = ? AND book_id = ?",
            [session["user_id"], book_id]
        ).fetchone()
    
    return render_template("book.html",
                           book=book,
                           rewiews=reviews,
                           avg_rating=avg_rating,
                            comments=comments,
                            user_review=user_review)