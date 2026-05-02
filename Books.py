import database as db

def get_all_books(query="", genre_id=None, offset=0, limit=None):
    sql = """SELECT DISTINCT books.id, books.title, books.author,
            books.year, books.created_by
            FROM books
            LEFT JOIN book_genres on books.id = book_genres.book_id
            where 1=1"""
    params = []
    if query:
        sql += " AND (LOWER(title) LIKE LOWER(?) OR LOWER(author) LIKE LOWER(?))"
        params.extend([f"%{query}%", f"%{query}%"])
    if genre_id:
        sql += " AND book_genres.genre_id =?"
        params.append(genre_id)
    sql += " ORDER BY title"
    if limit is not None:
        sql += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
    return db.query(sql, params)

def count_books(query="", genre_id=None):
    sql = """SELECT COUNT(DISTINCT books.id) AS cnt
             FROM books
             LEFT JOIN book_genres ON books.id = book_genres.book_id
             WHERE 1=1"""
    params = []
    if query:
        sql += " AND (LOWER(title) LIKE LOWER(?) OR LOWER(author) LIKE LOWER(?))"
        params.extend([f"%{query}%", f"%{query}%"])
    if genre_id:
        sql += " AND book_genres.genre_id = ?"
        params.append(genre_id)
    return db.query_one(sql, params)["cnt"]

def get_book(book_id):
    return db.query_one(
        "SELECT id, title, author, year, created_by FROM books WHERE id = ?",
        [book_id]
    )

def add_book(title, author, year, user_id, genre_ids):
    db.execute(
        "INSERT INTO books (title, author, year, created_by) VALUES (?, ?, ?, ?)",
        [title, author, year, user_id]
    )
    book_id = db.last_insert_id()
    for gid in genre_ids:
        db.execute(
            "INSERT INTO book_genres (book_id, genre_id) VALUES (?, ?)",
            [book_id, gid]
        )
    return book_id

def update_book(book_id, title, author, year, genre_ids):
    db.execute(
        "UPDATE books SET title = ?, author = ?, year = ? WHERE id = ?",
        [title, author, year, book_id]
    )
    db.execute(
        "DELETE FROM book_genres WHERE book_id = ?",
        [book_id]
    )
    for gid in genre_ids:
        db.execute(
            "INSERT INTO book_genres (book_id, genre_id) VALUES (?, ?)",
            [book_id, gid]
        )

def get_book_genre_ids(book_id):
    rows = db.query(
        "SELECT genre_id FROM book_genres WHERE book_id = ?",
        [book_id]
    )
    return [r["genre_id"] for r in rows]

def get_recent_books(limit=5):
    return db.query(
        "SELECT id, title, author, year, created_by FROM books ORDER BY id DESC LIMIT ?",
        [limit]
    )

def get_books_added_by(user_id):
    return db.query(
        "SELECT id, title, author, year FROM books WHERE created_by = ? ORDER BY year DESC",
        [user_id]
    )

def get_genres():
    return db.query("SELECT id, name FROM genres ORDER BY name")