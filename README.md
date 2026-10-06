# FastAPI Blog

A small FastAPI blog application that renders Jinja2 pages and exposes a JSON API.
Posts and users are stored in SQLite via SQLAlchemy, so data survives a restart.

## Requirements

- Python 3.10 or newer

## Setup

Create and activate a virtual environment, then install the app with its
dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

For the test suite:

```powershell
pip install -e ".[dev]"
```

Start the development server from the project root:

```powershell
uvicorn app.app:app --reload
```

Open <http://127.0.0.1:8000> in a browser. Interactive API documentation is
available at <http://127.0.0.1:8000/docs>.

The SQLite file `blog.db` is created automatically on first startup. Tables are
created with `create_all`, which never alters an existing table, so delete
`blog.db` after changing a column definition.

## Routes

### HTML pages

- `GET /` or `GET /posts` - Display all posts.
- `GET /posts/{post_id}` or `GET /{post_id}` - Display one post.
- `GET /users/{user_id}/posts` - Display one user's posts.

### JSON API

- `GET /api/posts` - Return all posts.
- `GET /api/posts/{post_id}` - Return one post.
- `POST /api/posts` - Create a post.
- `GET /api/users/{user_id}` - Return one user.
- `GET /api/users/{user_id}/posts` - Return one user's posts.
- `POST /api/users` - Create a user.

Example request:

```json
{
  "user_id": 1,
  "title": "My first post",
  "content": "Hello from the FastAPI blog."
}
```

## Tests

```powershell
pytest
```

## Project Structure

```text
app/app.py             FastAPI application and routes
app/database.py        Engine, session factory, and Base
app/models.py          SQLAlchemy User and Post models
app/schemas.py         Pydantic request and response models
templates/             Jinja2 HTML templates
static/                CSS, JavaScript, icons, and profile pictures
tests/                 Route and schema tests
pyproject.toml         Dependencies and tool configuration
```

## Notes

There is no authentication yet. `static/js/auth.js` calls `/api/users/me`, which
does not exist yet, and `POST /api/posts` takes `user_id` from the request body
instead of a session. Edit and delete controls on the post page are placeholders.