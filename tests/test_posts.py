"""Post creation, listing and ordering."""


def test_create_and_read_post(client, user):
    r = client.post(
        "/api/posts", json={"user_id": user["id"], "title": "T", "content": "C"}
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["author"]["username"] == "alex"

    assert client.get(f"/api/posts/{body['id']}").json()["title"] == "T"
    assert client.get(f"/api/users/{user['id']}/posts").json()[0]["title"] == "T"
    assert client.get("/api/posts/999999").status_code == 404
    assert client.get("/api/users/999999").status_code == 404


def test_create_post_requires_existing_user(client):
    r = client.post(
        "/api/posts", json={"user_id": 999999, "title": "T", "content": "C"}
    )
    assert r.status_code == 404


def test_posts_are_newest_first(client, user):
    ids = []
    for title in ("first", "second", "third"):
        r = client.post(
            "/api/posts", json={"user_id": user["id"], "title": title, "content": "c"}
        )
        ids.append(r.json()["id"])

    titles = [p["title"] for p in client.get("/api/posts").json()]
    assert titles[: len(ids)] == ["third", "second", "first"], titles


def test_dates_are_human_readable(client, user):
    r = client.post(
        "/api/posts", json={"user_id": user["id"], "title": "T", "content": "C"}
    )
    stamp = r.json()["date_posted"]
    assert "T" not in stamp, stamp

    assert stamp in client.get(f"/posts/{r.json()['id']}").text
