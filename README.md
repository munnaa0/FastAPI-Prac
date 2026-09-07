# FastAPI Blog

A small FastAPI blog application that renders Jinja2 pages and exposes a JSON API for posts. Posts are stored in memory, so data resets whenever the server restarts.

## Requirements

- Python 3.10 or newer

## Setup

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install fastapi uvicorn jinja2
```

Start the development server from the project root:

```powershell
uvicorn app.app:app --reload
```

Open <http://127.0.0.1:8000> in a browser. Interactive API documentation is available at <http://127.0.0.1:8000/docs>.

## Routes

### HTML pages

- `GET /` or `GET /posts` - Display all posts.
- `GET /{post_id}` or `GET /posts/{post_id}` - Display one post.

### JSON API

- `GET /api/posts` - Return all posts.
- `GET /api/posts/{post_id}` - Return one post.
- `POST /api/posts` - Create a post.

Example request:

```json
{
  "author": "Alex",
  "title": "My first post",
  "content": "Hello from the FastAPI blog."
}
```

## Project Structure

```text
app/app.py             FastAPI application and routes
templates/             Jinja2 HTML templates
static/                CSS, JavaScript, icons, and profile pictures
schemas.py             Pydantic request and response models
pyproject.toml         Tool configuration
```

## Notes

Authentication links and some frontend behavior are placeholders. The app currently uses an in-memory list instead of a database.
