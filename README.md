# Booktracking
Small test webapp to let users track and review books they have read.\
This will be somewhat of a community project where the user can add books that are missing and then review and comment on other peoples additions. A Good Reads for the people by the people\
**Implemented features**\
-Account creation, login, logout\
-Searching for books by title, author and genre\
-adding books\
-Adding and editing Books that dont exist in database yet\
-making, editing deleting reviews and comments\
-User profile page with user statistics\

## Setup

**Requirements**
- Python 3
- Flask
- Werkzeug

**Installation**
1. Clone the repository
2. Create a virtual environment and activate it:
```
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Mac/Linux
```
3. Install flask:
```
    pip install flask
```
4. Create a `config.py` file based on the example:
```
   cp config.py.example config.py
```
   Then open `config.py` and change the secret key to any random string.

5. Initialize the database:
```
    flask init-db
```
6. Run the app:
```
    flask run
```
7. Flask will print you a URL in the terminal, open it in your browser.

**Note:** `database.db` is not included in the repository. The database is created locally when you run `flask init-db`.

## Testing the Application

1. Register a new account.
2. Add a few books, selecting one or more genres.
3. Search books by title, author, or filter by genre.
4. Visit a book page and leave a review with a rating.
5. On any review, add a comment.
6. Go to your user profile by clicking on a review or comment to see your stats and added books.
7. Edit or delete your own content.

## Testing with large data

A `seed.py` script is provided to insert 10 000 users, 50 000 books, and numerous reviews and comments.
Run it and then test the app as usual

## Personal Large-data tests

After inserting a large amount of data the app remains perfectly responsive:
All pages including the search function load near instantly there is not much to say besides that

## Code quality

The code fulfills all pylint criteria receiving a 10/10 and is clean enough.