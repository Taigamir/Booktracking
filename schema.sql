CREATE TABLE Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE Books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Title TEXT NOT NULL,
    Author TEXT NOT NULL,
    Year INTEGER
    created INTEGER,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE Genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE Book_Genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Book_id INTEGER NOT NULL,
    Genre_id INTEGER NOT NULL,
    PRIMARY KEY (Book_id, Genre_id),
    FOREIGN KEY (Book_id) REFERENCES Books(id),
    FOREIGN KEY (Genre_id) REFERENCES Genres(id)
);

CREATE TABLE Reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    User_id INTEGER NOT NULL,
    Book_id INTEGER NOT NULL,
    Rating INTEGER NOT NULL CHECK(Rating => 1 AND Rating <= 5),
    Content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (User_id) REFERENCES Users(id),
    FOREIGN KEY (Books_id) REFERENCES Books(id)
);

CREATE TABLE Comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    User_id INTEGER NOT NULL,
    Review_id INTEGER NOT NULL,
    Content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (User_id) REFERENCES Users(id),
    FOREIGN KEY (Review_id) REFERENCES Reviews(id)
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