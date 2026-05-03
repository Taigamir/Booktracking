# Pylint report – BookReviews

## Final score: 10/10

## Summary of improvements

The initial Pylint score was **6.76**. The following issues were identified and fixed:

### Fixed issues

- **Unused imports** – removed `abort`, `database as db` from `app.py`, `sqlite3` from `users.py`.
- **Missing module and function docstrings** – added concise docstrings to every module and every function.
- **Dangerous default arguments** – replaced `params=[]` with `params=None` in `database.py` and handled it safely.
- **Inconsistent return statements** – added an explicit `return None` in `csrf_protect` when no CSRF violation occurs.
- **Redefining outer names** – renamed shadowed variables (`book` → `book_data`) to avoid confusion.
- **Unused variable** – removed the unnecessary assignment in `add_comment`.
- **Trailing whitespace and missing final newlines** – cleaned all files.
- **Line too long** – split a long SQL string in `reviews.py` across two lines.
- **String statement not docstring** – moved all module docstrings to be the very first line of each file, ensuring they are correctly recognised as docstrings.

### After fixes
## the most recent version pylint test
```
-------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 9.63/10, +0.37)
```