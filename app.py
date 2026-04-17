import sqlite3
import database as db
from flask import Flask
from flask import render_template, request, redirect, g, session
from werkzeug.security import generate_password_hash, check_password_hash

import config

app = Flask(__name__)
app.secret_key = config.secret_key


@app.cli.command("init-db")
def init_db_command():
    init_db(app)
    print("Database init")

@app.route("/")
def index():
    recent_books = db.query(
        "SELECT * FROM books ORDER BY id DESC LIMIT 5"
    )
    recent_reviews = db.query(
        """SELECT reviews.*, books.title, users.username
            FROM reviews
            JOIN books ON reviews.book_id = books.id
            JOIN users ON reviews.user_id = users.id
            ORDER BY reviews.created_at DESC LIMIT 5"""
    )
    return render_template("index.html",
                           recent_books=recent_books,
                           recent_reviews=recent_reviews)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match")
        
        password_hash = generate_password_hash(password)
        try:
            db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    [username, password_hash])
        except sqlite3.IntegrityError:
            return render_template("register.html", error="Username already taken")
        
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = db.query_one("SELECT * FROM users WHERE username = ?",
                          [username])
        
        print("USER FOUND:", user)
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            print("SESSION SET:", session)
            return redirect("/")
        return render_template("login.html", error="Wrong username or password")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/books")
def books():
    query = request.args.get("query", "")

    if query:
        results = db.query(
            """SELECT * FROM books
                WHERE LOWER(title) LIKE LOWER(?)
                OR LOWER(author) LIKE LOWER(?)""",
            [f"%{query}%", f"%{query}%"]
        )
    else:
        results = db.query("SELECT * FROM books")

    return render_template("books.html", books=results, query=query)

@app.route("/user/<int:user_id>")
def user_profile(user_id):
    user = db.query_one(
        """SELECT 
                id, 
                username, 
                DATE(created_as) as join_date
            FROM users 
            WHERE id = ?""", 
        [user_id]
    )
    if not user:
        return "Usernot found", 404 
    stats = db.query_one(
        """SELECT
            COUNT(DISTINCT r.id) as reviews_written,
            COUNT(DISTINCT c.id) as comments_written,
            ROUND(AVG(r.rating), 1) as avg_rating
        FROM users u
        LEFT JOIN reviews r on r.user_id = u.id
        LEFT JOIN comments c on c.user_id = u.id
        WHERE u.id = ? 
        """, [user_id]
    )
    reviews = db.query(
        """SELECT reviews.*, books.title
            FROM reviews
            JOIN books ON reviews.book_id = books.id
            WHERE reviews.user_id = ?
            ORDER BY reviews.crated_at DESC
            LIMIT 5""",
        [user_id]
    )
    return render_template("user.html",
                           user=user,
                           stats=stats,
                           reviews=reviews)

@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if not session.get("user_id"):
        return redirect("/login")
    
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        year = request.form["year"] or None
        db.execute(
            "INSERT INTO books (title, author, year, created_by) VALUES (?, ?, ?, ?)",
            [title, author, year, session["user_id"]]
        )
        book = db.query_one(
            "SELECT * FROM books WHERE title = ? AND created_by = ? ORDER BY id DESC LIMIT 1",
            [title, session["user_id"]]
        )
        if not book:
            return redirect("/books")
        return redirect(f"/book/{book['id']}")
    
    query = request.args.get("query", "")
    return render_template("add_book.html", query=query)

@app.route("/edit_book/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    if not session.get("user_id"):
        return redirect("/login")
    
    book = db.query_one(
        "SELECT * FROM books WHERE id = ?", [book_id]
    )

    if not book or book["created_by"] != session["user_id"]:
        return redirect("/books")

    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        year = request.form["year"] or None
        db.execute(
            "UPDATE books SET title = ?, author = ?, year = ? WHERE id = ?",
            [title, author, year, book_id]
        )
        return redirect(f"/book/{book_id}")
    
    return render_template("edit_book.html", book=book)


@app.route("/book/<int:book_id>")
def book(book_id):
    book = db.query_one(
        "SELECT * FROM books WHERE id = ?", [book_id]
    )
    if not book:
        return redirect("/books")
    
    reviews = db.query(
        """SELECT reviews.*, users.username
            FROM reviews
            JOIN users ON reviews.user_id = users.id
            WHERE reviews.book_id = ?
            ORDER BY reviews.created_at DESC""",
        [book_id]
    )

    avg_rating = db.query_one(
        "SELECT ROUND(AVG(rating), 1) as avg FROM reviews WHERE book_id = ?",
        [book_id]
    )

    comments = db.query(
        """SELECT comments.*, users.username
            FROM comments
            JOIN users ON comments.user_id = users.id
            WHERE comments.review_id IN(
                SELECT id FROM reviews WHERE book_id = ?
            )
            ORDER BY comments.created_at ASC""",
            [book_id]
    )

    user_review = None
    if session.get("user_id"):
        user_review = db.query_one(
            "SELECT * FROM reviews WHERE user_id = ? AND book_id = ?",
            [session["user_id"], book_id]
        )
    
    return render_template("book.html",
                           book=book,
                           reviews=reviews,
                           avg_rating=avg_rating,
                            comments=comments,
                            user_review=user_review)

@app.route("/add_review/<int:book_id>", methods=["POST"])
def add_review(book_id):
    if not session.get("user_id"):
        return redirect("/login")
    
    rating = request.form["rating"]
    content = request.form["content"]
    db.execute(
        "INSERT INTO reviews (user_id, book_id, rating, content) VALUES (?, ?, ?, ?)",
        [session["user_id"], book_id, rating, content]
    )
    return redirect(f"/book/{book_id}")

@app.route("/edit_review/<int:review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    if not session.get("user_id"):
        return redirect("/login")

    review = db.query_one(
        "SELECT * FROM reviews WHERE id = ?", [review_id]
    )

    if not review or review["user_id"] != session["user_id"]:
        return redirect("/books")
    
    if request.method == "POST":
        rating = request.form["rating"]
        content = request.form["content"]
        db.execute(
            "UPDATE reviews SET rating = ?, content = ? where id = ?",
            [rating, content, review_id]
        )
        return redirect(f"/book/{review['book_id']}")
    return render_template("edit_review.html", review=review)

@app.route("/delete_review/<int:review_id>")
def delete_review(review_id):
    if not session.get("user_id"):
        return redirect("/login")
    
    review = db.query_one(
        "SELECT * FROM reviews WHERE id = ?", [review_id]
    )

    if not review or review["user_id"] != session["user_id"]:
        return redirect("/books")
    
    db.execute("DELETE FROM reviews WHERE id = ?", [review_id])
    return redirect(f"/book/{review['book_id']}")

@app.route("/add_comment/<int:review_id>", methods=["POST"])
def add_comment(review_id):
    if not session.get("user_id"):
        return redirect("/login")

    content = request.form["content"]
    review = db.query_one(
        "SELECT * FROM reviews WHERE id = ?", [review_id]
    )

    db.execute(
        "INSERT INTO comments (user_id, review_id, content) VALUES (?, ?, ?)",
        [session["user_id"], review_id, content]
    )
    return redirect(f"/book/{review['book_id']}")

@app.route("/edit_comment/<int:comment_id>", methods=["GET", "POST"])
def edit_comment(comment_id):
    if not session.get("user_id"):
        return redirect("/login")

    comment = db.query_one(
        """SELECT comments.*, reviews.book_id
            FROM comments
            JOIN reviews ON comments.review_id = reviews.id
            WHERE comments.id = ?""",
            [comment_id]
    )
    if not comment or comment["user_id"] != session["user_id"]:
        return redirect("/books")
    
    if request.method == "POST":
        content = request.form["content"]
        db.execute(
            "UPDATE comments SET content = ? where id = ?",
            [content, comment_id]
        )
        return redirect(f"/book/{comment['book_id']}")
    return render_template("edit_comment.html", comment=comment)

@app.route("/delete_comment/<int:comment_id>")
def delete_comment(comment_id):
    if not session.get("user_id"):
        return redirect("/login")
    
    comment = db.query_one(
        "SELECT comments.*, reviews.book_id FROM comments JOIN reviews ON comments.review_id = reviews.id WHERE comments.id = ?",
        [comment_id]
    )

    if not comment or comment["user_id"] != session["user_id"]:
        return redirect("/books")
    
    db.execute("DELETE FROM comments WHERE id = ?", [comment_id])
    return redirect(f"/book/{comment['book_id']}")

if __name__ == "__main__":
    app.run(debug=True)