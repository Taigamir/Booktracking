CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    year INTEGER
    created INTEGER,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE book_Genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    PRIMARY KEY (book_id, genre_id),
    FOREIGN KEY (book_id) REFERENCES books(id),
    FOREIGN KEY (genre_id) REFERENCES genres(id)
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK(rating => 1 AND rating <= 5),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (books_id) REFERENCES books(id)
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    review_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (review_id) REFERENCES reviews(id)
);

INSERT INTO genres (name) VALUES
    ('Fiction')
    ('Non-fiction')
    ('Sci-fi')
    ('Fantasy')
    ('Thriller')
    ('Romance')
    ('Mystery')
    ('Horror')
    ('Historical')
    ('Biography');