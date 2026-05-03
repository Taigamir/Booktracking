"""Insert thousands of test records for performance evaluation."""
import sqlite3
import random

DUMMY_HASH = "pbkdf2:sha256:260000$dummy$..."

con = sqlite3.connect("database.db")
con.execute("PRAGMA foreign_keys = ON")
cur = con.cursor()

cur.execute("BEGIN TRANSACTION")

print("Inserting users...")
for i in range(10000):
    cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (f"testuser{i}", DUMMY_HASH))

print("Inserting books...")
for i in range(50000):
    year = 1900 + (i % 200)
    user_id = random.randint(1, 10000)
    cur.execute("INSERT INTO books (title, author, year, created_by) VALUES (?, ?, ?, ?)",
                (f"Book {i}", f"Author {i % 1000}", year, user_id))
    book_id = cur.lastrowid
    num_genres = random.randint(1, 3)
    genres = random.sample(range(1, 11), num_genres)
    for gid in genres:
        cur.execute("INSERT INTO book_genres (book_id, genre_id) VALUES (?, ?)",
                    (book_id, gid))

print("Inserting reviews...")
for user_id in range(1, 10001):
    for _ in range(random.randint(0, 4)):
        book_id = random.randint(1, 50000)
        rating = random.randint(1, 5)
        cur.execute("INSERT INTO reviews (user_id, book_id, rating, content) VALUES (?, ?, ?, ?)",
                    (user_id, book_id, rating, "Sample review text."))

print("Inserting comments...")
cur.execute("SELECT id FROM reviews")
review_ids = [row[0] for row in cur.fetchall()]
for review_id in review_ids[::5]:
    user_id = random.randint(1, 10000)
    cur.execute("INSERT INTO comments (user_id, review_id, content) VALUES (?, ?, ?)",
                (user_id, review_id, "Sample comment."))

cur.execute("COMMIT")
con.close()
print("Done. Database seeded.")