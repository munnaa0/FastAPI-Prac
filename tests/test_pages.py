"""The Jinja2 pages served by the app."""

import pytest


@pytest.mark.parametrize("path", ["/", "/posts"])
def test_list_pages_render(client, user, post, path):
    r = client.get(path)
    assert r.status_code == 200
    assert user["username"] in r.text
    assert "<app.models.User object" not in r.text


@pytest.mark.parametrize("path", ["/{id}", "/posts/{id}"])
def test_post_page_renders(client, post, path):
    r = client.get(path.format(id=post["id"]))
    assert r.status_code == 200
    assert post["title"] in r.text


def test_user_posts_page_renders(client, user, post):
    r = client.get(f"/users/{user['id']}/posts")
    assert r.status_code == 200
    assert user["username"] in r.text


def test_missing_post_page_404s(client):
    assert client.get("/posts/999999").status_code == 404


def test_post_page_renders_the_post_forms(client, post):
    text = client.get(f"/posts/{post['id']}").text
    # New Post modal lives in layout.html, the edit/delete ones in post.html.
    assert 'id="createPostForm"' in text
    assert 'id="editPostForm"' in text
    assert 'id="confirmDelete"' in text
