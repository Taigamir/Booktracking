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
    return render_template(index.html)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["Username"]
        password1 = request.form["Password1"]
        password2 = request.form["Password2"]
        if password1 != password2:
            return "ERROR: The passwords dont match"
        password_hash = generate_password_hash(password1)
        db = get_db()
        try:
            db.execute("INSERT INTO users (usernam, password_hash) VALUES (?, ?)",
                    [username, password_hash])
            db.commit()
        except sqlite3.IntegrityError:
            return "ERROR: account already exists"
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