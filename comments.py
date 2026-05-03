"""Data access module for comments"""
import database as db
def get_comments_for_book(book_id):
    """Gets all comments under a book"""
    return db.query(
        """SELECT comments.id, comments.user_id, comments.review_id,
                  comments.content, comments.created_at,
                  users.username
           FROM comments
           JOIN users ON comments.user_id = users.id
           WHERE comments.review_id IN (
               SELECT id FROM reviews WHERE book_id = ?
           )
           ORDER BY comments.created_at ASC""",
        [book_id]
    )

def add_comment(user_id, review_id, content):
    """Adds comment to db"""
    db.execute(
        "INSERT INTO comments (user_id, review_id, content) VALUES (?, ?, ?)",
        [user_id, review_id, content]
    )

def get_comment(comment_id):
    """Returns a specific comment"""
    return db.query_one(
        """SELECT comments.id, comments.user_id, comments.review_id,
                  comments.content, comments.created_at,
                  reviews.book_id
           FROM comments
           JOIN reviews ON comments.review_id = reviews.id
           WHERE comments.id = ?""",
        [comment_id]
    )

def update_comment(comment_id, content):
    """Updates exisitng comment"""
    db.execute(
        "UPDATE comments SET content = ? WHERE id = ?",
        [content, comment_id]
    )

def delete_comment(comment_id):
    """Deletes comment from db"""
    db.execute("DELETE FROM comments WHERE id = ?", [comment_id])
