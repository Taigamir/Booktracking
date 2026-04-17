# Booktracking
Small test webapp to let users track and review books they have read.\
This will be somewhat of a community project where the user can add books that are missing and then review and comment on other peoples additions. A Good Reads for the people by the people\
**Implemented features**\
-Account creation, login, logout\
-Searching for books\
-adding books\
-Adding and editing Books that dont exist in database yet\
-making, editing deleting reviews and comments\
-User profile page with user statistics\

**Features still in development:**\
-add more details = (picture, description, tags)\
-sort search funtion by tags\
-more freedom for reviews/comments = (pictures?)\
-TBR, read, reading shelves?\
-friends list?, messaging and sharing?\

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