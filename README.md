# FastAPI Blog

A small FastAPI blog: Jinja2 HTML pages on the front, a JSON API underneath,
SQLite through SQLAlchemy for storage.

## Requirements

- Python 3.10 or newer

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

Start the development server from the project root:

```powershell
uvicorn app.app:app --reload
```

- Site: <http://127.0.0.1:8000>
- API docs: <http://127.0.0.1:8000/docs>

Tables are created on startup. Point `DATABASE_URL` at another SQLite file to
use a different database; it defaults to `./blog.db`.

## Routes

### HTML pages

- `GET /` or `GET /posts` - all posts, newest first
- `GET /{post_id}` or `GET /posts/{post_id}` - one post (404 page if missing)
- `GET /users/{user_id}/posts` - one user's posts

### JSON API

- `POST /api/users` - create a user (`201`, `400` if username or email is taken)
- `GET /api/users/{user_id}` - one user
- `GET /api/posts` - all posts, newest first
- `POST /api/posts` - create a post (`201`)
- `GET /api/posts/{post_id}` - one post
- `GET /api/{user_id}/posts` - one user's posts

Creating a post requires an existing `user_id`:

```json
{
  "user_id": 1,
  "title": "My first post",
  "content": "Hello from the FastAPI blog."
}
```

## Layout

```text
app/app.py         routes, templates, mounts
app/database.py    engine, session factory, get_db dependency
app/models.py      User and Post tables
app/schemas.py     Pydantic request/response models, friendly_date
templates/         Jinja2 HTML templates
static/            CSS, JavaScript, icons
media/             uploaded profile pictures
notes/             scratch files
tests/             smoke tests
```

## Tests

```powershell
pytest tests -q
ruff check app
```

Tests set `DATABASE_URL` to a temp file before importing the app, so
`blog.db` is never touched.

## Notes

No authentication yet - posts are created by passing any `user_id`.
