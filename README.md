# FastAPI Blog

A small FastAPI blog: Jinja2 HTML pages on the front, a JSON API underneath,
SQLite through SQLAlchemy for storage.

## Requirements

- Python 3.10 or newer

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Start the development server from the project root:

```powershell
uvicorn app.main:app --reload
```

- Site: <http://127.0.0.1:8000>
- API docs: <http://127.0.0.1:8000/docs>

Tables are created on startup. Point `DATABASE_URL` at another SQLite file to
use a different database; it defaults to `blog.db` in the project root.

## Routes

### HTML pages

- `GET /` or `GET /posts` - all posts, newest first
- `GET /{post_id}` or `GET /posts/{post_id}` - one post (404 page if missing)
- `GET /users/{user_id}/posts` - one user's posts

### JSON API

- `POST /api/users` - create a user (`201`, `400` if username or email is taken)
- `GET /api/users/{user_id}` - one user
- `PATCH /api/users/{user_id}` - update a user
- `DELETE /api/users/{user_id}` - delete a user (`204`)
- `GET /api/posts` - all posts, newest first
- `POST /api/posts` - create a post (`201`)
- `GET /api/posts/{post_id}` - one post
- `PUT /api/posts/{post_id}` - replace a post
- `PATCH /api/posts/{post_id}` - update a post
- `DELETE /api/posts/{post_id}` - delete a post (`204`)

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
app/main.py        routes, templates, mounts
app/config.py      settings loaded from .env
app/database.py    engine, session factory, get_db dependency
app/models.py      User and Post tables
app/schemas.py     Pydantic request/response models
app/auth.py        password hashing and JWT helpers
app/utils.py       friendly_date, shared by schemas and the templates
app/routers/       users and posts routers
app/templates/     Jinja2 HTML templates
app/static/        CSS, JavaScript, icons
media/             uploaded profile pictures
notes/             scratch files
tests/             pytest suite
```

## Tests

```powershell
pytest tests -q
ruff check app tests
ruff format app tests
```

Tests set `DATABASE_URL` to a temp file before importing the app, so
`blog.db` is never touched.

## Notes

Authentication is a work in progress. `app/auth.py` has password hashing and
JWT helpers, but there is no token endpoint yet and `password_hash` is still
stored empty - posts are created by passing any `user_id`.
