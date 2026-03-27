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
        password = request.form["Password"]
        password_hash = generate_password_hash(password)
        db = get_db()
        db.execute("INSERT INTO users (usernam, password_hash) VALUES (?, ?)",
                   [username, password_hash])
        db.commit()
        return redirect("/login")
    return render_template("register.html")
