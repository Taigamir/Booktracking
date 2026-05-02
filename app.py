import secrets
import sqlite3

import click
from flask import Flask, g, redirect, render_template, request, session
from flask.cli import with_appcontext

import config
import database as db
import Books
import reviews
import comments
import users

app = Flask(__name__)
app.secret_key = config.secret_key

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(16)
    return session['_csrf_token']
app.jinja_env.globals['csrf_token'] = generate_csrf_token

@app.cli.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    con = sqlite3.connect('database.db')
    with app.open_resource('schema.sql', mode='r') as f:
        con.executescript(f.read())
    con.commit()
    con.close()
    click.echo('Initialized the database')

@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.get('_csrf_token')
        form_token = request.form.get('_csrf_token')
        if not token or token != form_token:
            return "CSRF token missing or incorrect, 400"
        

@app.route("/")
def index():
    recent_books = Books.get_recent_books(5)
    recent_reviews = reviews.get_recent_reviews(5)
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
        try:
            users.create_user(username, password)
        except sqlite3.IntegrityError:
            return render_template("register.html", error="Username already taken")
        
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = users.check_login(username, password)
        if user:
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
    query = request.args.get("query", "")
    genre_id = request.args.get("genre_id", type=int)
    page = request.args.get("page", 1, type=int)
    per_page = 10

    total = Books.count_books(query, genre_id)
    offset = (page-1) * per_page
    results = Books.get_all_books(query, genre_id, offset, per_page)
    genres = Books.get_genres()
    total_pages = max(1, (total + per_page - 1) // per_page)

    return render_template(
        "books.html",
        books=results, 
        query=query,
        genres=genres,
        selected_genre=genre_id,
        current_page=page,
        total_pages=total_pages)

@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if not session.get("user_id"):
        return redirect("/login")
    
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        year = request.form["year"] or None
        genre_ids = request.form.getlist("genre_ids")
        book_id = Books.add_book(title, author, year, session["user_id"], genre_ids)
        return redirect(f"/book/{book_id}")
    
    query = request.args.get("query", "")
    genres = Books.get_genres()
    return render_template("add_book.html", query=query, genres=genres)

@app.route("/edit_book/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    if not session.get("user_id"):
        return redirect("/login")
    
    book = Books.get_book(book_id)
    if not book or book["created_by"] != session["user_id"]:
        return redirect("/books")
    
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        year = request.form["year"] or None
        genre_ids = request.form.getlist("genre_ids")
        Books.update_book(book_id, title, author, year, genre_ids)
        return redirect(f"/book/{book_id}")
    
    selected_genre_ids = Books.get_book_genre_ids(book_id)
    all_genres = Books.get_genres()
    
    return render_template(
            "edit_book.html", 
            book=book, 
            genres=all_genres, 
            selected_genre_ids=selected_genre_ids)


@app.route("/book/<int:book_id>")
def book(book_id):
    book = Books.get_book(book_id)
    if not book:
        return redirect("/books")
    reviews_list = reviews.get_reviews_for_book(book_id)
    avg_rating = reviews.get_avg_rating(book_id)
    comments_list = comments.get_comments_for_book(book_id)

    user_review = None
    if session.get("user_id"):
        user_review = reviews.get_user_review(session["user_id"], book_id)
    
    return render_template(
            "book.html",
            book=book,
            reviews=reviews_list,
            avg_rating=avg_rating,
            comments=comments_list,
            user_review=user_review)

@app.route("/add_review/<int:book_id>", methods=["POST"])
def add_review(book_id):
    if not session.get("user_id"):
        return redirect("/login")
    
    rating = request.form["rating"]
    content = request.form["content"]
    reviews.add_review(session["user_id"], book_id, rating, content)
    return redirect(f"/book/{book_id}")

@app.route("/edit_review/<int:review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    if not session.get("user_id"):
        return redirect("/login")

    review = reviews.get_review(review_id)
    if not review or review["user_id"] != session["user_id"]:
        return redirect("/books")
    
    if request.method == "POST":
        rating = request.form["rating"]
        content = request.form["content"]
        reviews.update_review(review_id, rating, content)
        return redirect(f"/book/{review['book_id']}")
    return render_template("edit_review.html", review=review)

@app.route("/delete_review/<int:review_id>")
def delete_review(review_id):
    if not session.get("user_id"):
        return redirect("/login")
    
    review = reviews.get_review(review_id)
    if not review or review["user_id"] != session["user_id"]:
        return redirect("/books")
    reviews.delete_review(review_id)
    return redirect(f"/book/{review['book_id']}")

@app.route("/add_comment/<int:review_id>", methods=["POST"])
def add_comment(review_id):
    if not session.get("user_id"):
        return redirect("/login")

    content = request.form["content"]
    comment = comments.add_comment(session["user_id"], review_id, content)
    review = reviews.get_review(review_id)
    return redirect(f"/book/{review['book_id']}")

@app.route("/edit_comment/<int:comment_id>", methods=["GET", "POST"])
def edit_comment(comment_id):
    if not session.get("user_id"):
        return redirect("/login")

    com = comments.get_comment(comment_id)
    if not com or com["user_id"] != session["user_id"]:
        return redirect("/books")
    
    if request.method == "POST":
        content = request.form["content"]
        comments.update_comment(comment_id, content)
        return redirect(f"/book/{com['book_id']}")
    return render_template("edit_comment.html", comment=com)

@app.route("/delete_comment/<int:comment_id>")
def delete_comment(comment_id):
    if not session.get("user_id"):
        return redirect("/login")
    
    com = comments.get_comment(comment_id)

    if not com or com["user_id"] != session["user_id"]:
        return redirect("/books")
    comments.delete_comment(comment_id)
    return redirect(f"/book/{com['book_id']}")

@app.route("/user/<int:user_id>")
def user_profile(user_id):
    user = users.get_user(user_id)
    if not user:
        return "Usernot found", 404 
    stats = users.get_user_stats(user_id)
    recent_reviews = reviews.get_user_reviews(user_id, limit=5)
    books_added = Books.get_books_added_by(user_id)
    return render_template("user.html",
            user=user,
            stats=stats,
            reviews=recent_reviews,
            books_added=books_added
    )

if __name__ == "__main__":
    app.run(debug=True)