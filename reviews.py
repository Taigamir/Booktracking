import database as db

import database as db

def get_reviews_for_book(book_id):
    return db.query(
        """SELECT reviews.id, reviews.user_id, reviews.book_id,
                  reviews.rating, reviews.content, reviews.created_at,
                  users.username
           FROM reviews
           JOIN users ON reviews.user_id = users.id
           WHERE reviews.book_id = ?
           ORDER BY reviews.created_at DESC""",
        [book_id]
    )

def get_user_review(user_id, book_id):
    return db.query_one(
        "SELECT id, user_id, book_id, rating, content, created_at FROM reviews WHERE user_id = ? AND book_id = ?",
        [user_id, book_id]
    )

def add_review(user_id, book_id, rating, content):
    db.execute(
        "INSERT INTO reviews (user_id, book_id, rating, content) VALUES (?, ?, ?, ?)",
        [user_id, book_id, rating, content]
    )

def get_review(review_id):
    return db.query_one(
        "SELECT id, user_id, book_id, rating, content, created_at FROM reviews WHERE id = ?",
        [review_id]
    )

def update_review(review_id, rating, content):
    db.execute(
        "UPDATE reviews SET rating = ?, content = ? WHERE id = ?",
        [rating, content, review_id]
    )

def delete_review(review_id):
    db.execute("DELETE FROM reviews WHERE id = ?", [review_id])

def get_avg_rating(book_id):
    result = db.query_one(
        "SELECT ROUND(AVG(rating), 1) AS avg FROM reviews WHERE book_id = ?",
        [book_id]
    )
    return result["avg"] if result else None

def get_recent_reviews(limit=5):
    return db.query(
        """SELECT reviews.id, reviews.user_id, reviews.book_id,
                  reviews.rating, reviews.content, reviews.created_at,
                  books.title, users.username
           FROM reviews
           JOIN books ON reviews.book_id = books.id
           JOIN users ON reviews.user_id = users.id
           ORDER BY reviews.created_at DESC LIMIT ?""",
        [limit]
    )

def get_user_reviews(user_id, limit=5):
    return db.query(
        """SELECT reviews.id, reviews.user_id, reviews.book_id,
                  reviews.rating, reviews.content, reviews.created_at,
                  books.title
           FROM reviews
           JOIN books ON reviews.book_id = books.id
           WHERE reviews.user_id = ?
           ORDER BY reviews.created_at DESC
           LIMIT ?""",
        [user_id, limit]
    )