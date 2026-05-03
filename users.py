from werkzeug.security import generate_password_hash, check_password_hash
import database as db
"""Handles all data related to users"""
def create_user(username, password):
    """Adds new user to db"""
    password_hash = generate_password_hash(password)
    db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        [username, password_hash]
    )

def check_login(username, password):
    """Checks if user logged in"""
    user = db.query_one(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        [username]
    )
    if user and check_password_hash(user["password_hash"], password):
        return {"id": user["id"], "username": user["username"]}
    return None

def get_user(user_id):
    """Gets base user data"""
    return db.query_one(
        "SELECT id, username, DATE(created_at) AS join_date FROM users WHERE id = ?",
        [user_id]
    )

def get_user_stats(user_id):
    """Returns specific user statistics"""
    return db.query_one(
        """SELECT
            COUNT(DISTINCT b.id)        AS books_added,
            COUNT(DISTINCT r.id)        AS reviews_written,
            COUNT(DISTINCT c.id)        AS comments_written,
            ROUND(AVG(r.rating), 1)     AS avg_rating
           FROM users u
           LEFT JOIN books b  ON b.created_by = u.id
           LEFT JOIN reviews r ON r.user_id = u.id
           LEFT JOIN comments c ON c.user_id = u.id
           WHERE u.id = ?""",
        [user_id]
    )
