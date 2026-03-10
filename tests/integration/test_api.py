"""Integration tests for Flask API endpoints."""

import json
import pytest

pytestmark = pytest.mark.integration


class TestSnippetAPI:
    """Tests for snippet CRUD API endpoints."""

    def test_create_snippet(self, client):
        resp = client.post("/api/snippets", json={
            "title": "Hello",
            "code": "print('hello')",
            "language": "python",
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["title"] == "Hello"
        assert data["id"] is not None

    def test_list_snippets(self, client):
        client.post("/api/snippets", json={"title": "A"})
        client.post("/api/snippets", json={"title": "B"})
        resp = client.get("/api/snippets")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 2

    def test_get_snippet(self, client, sample_snippet):
        resp = client.get(f"/api/snippets/{sample_snippet['id']}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["title"] == "Hello World"

    def test_get_snippet_not_found(self, client):
        resp = client.get("/api/snippets/nonexistent")
        assert resp.status_code == 404

    def test_update_snippet(self, client, sample_snippet):
        resp = client.put(f"/api/snippets/{sample_snippet['id']}", json={"title": "Updated"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["title"] == "Updated"

    def test_update_creates_version(self, client, sample_snippet):
        client.put(f"/api/snippets/{sample_snippet['id']}", json={"title": "V2"})
        resp = client.get(f"/api/snippets/{sample_snippet['id']}/versions")
        data = resp.get_json()
        assert len(data) == 1

    def test_delete_snippet(self, client, sample_snippet):
        resp = client.delete(f"/api/snippets/{sample_snippet['id']}")
        assert resp.status_code == 200
        assert resp.get_json()["ok"] is True
        # Verify deleted
        resp2 = client.get(f"/api/snippets/{sample_snippet['id']}")
        assert resp2.status_code == 404

    def test_filter_by_visibility(self, client):
        client.post("/api/snippets", json={"title": "Pub", "visibility": "public"})
        client.post("/api/snippets", json={"title": "Priv", "visibility": "private"})
        resp = client.get("/api/snippets?visibility=public")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "Pub"

    def test_filter_by_language(self, client):
        client.post("/api/snippets", json={"title": "Py", "language": "python", "code": "x"})
        client.post("/api/snippets", json={"title": "JS", "language": "javascript", "code": "y"})
        resp = client.get("/api/snippets?language=python")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "Py"


class TestStarAPI:
    """Tests for star/favorite API."""

    def test_toggle_star(self, client, sample_snippet):
        resp = client.post(f"/api/snippets/{sample_snippet['id']}/star")
        assert resp.status_code == 200
        assert resp.get_json()["starred"] is True

        resp2 = client.post(f"/api/snippets/{sample_snippet['id']}/star")
        assert resp2.get_json()["starred"] is False

    def test_filter_starred(self, client, sample_snippet):
        client.post(f"/api/snippets/{sample_snippet['id']}/star")
        resp = client.get("/api/snippets?starred=1")
        data = resp.get_json()
        assert len(data) == 1


class TestForkAPI:
    """Tests for fork API."""

    def test_fork_snippet(self, client, sample_snippet):
        resp = client.post(f"/api/snippets/{sample_snippet['id']}/fork")
        assert resp.status_code == 201
        data = resp.get_json()
        assert "fork" in data["title"].lower()
        assert data["fork_of"] == sample_snippet["id"]

    def test_fork_nonexistent(self, client):
        resp = client.post("/api/snippets/nope/fork")
        assert resp.status_code == 404


class TestSearchAPI:
    """Tests for search API."""

    def test_search_by_title(self, client):
        client.post("/api/snippets", json={"title": "Flask Guide", "code": "x"})
        client.post("/api/snippets", json={"title": "React Tips", "code": "y"})
        resp = client.get("/api/snippets/search?q=flask")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "Flask Guide"

    def test_search_by_code(self, client):
        client.post("/api/snippets", json={"title": "T", "code": "def fibonacci(n): pass"})
        resp = client.get("/api/snippets/search?q=fibonacci")
        data = resp.get_json()
        assert len(data) == 1


class TestSlugAPI:
    """Tests for slug-based snippet access."""

    def test_get_by_slug(self, client, sample_snippet):
        resp = client.get(f"/api/snippets/slug/{sample_snippet['slug']}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["title"] == "Hello World"

    def test_slug_not_found(self, client):
        resp = client.get("/api/snippets/slug/nosuchslug")
        assert resp.status_code == 404


class TestCollectionAPI:
    """Tests for collection API endpoints."""

    def test_create_collection(self, client):
        resp = client.post("/api/collections", json={"name": "Python"})
        assert resp.status_code == 201
        assert resp.get_json()["name"] == "Python"

    def test_list_collections(self, client):
        client.post("/api/collections", json={"name": "A"})
        client.post("/api/collections", json={"name": "B"})
        resp = client.get("/api/collections")
        assert len(resp.get_json()) == 2

    def test_update_collection(self, client, sample_collection):
        resp = client.put(f"/api/collections/{sample_collection['id']}", json={"name": "New"})
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "New"

    def test_delete_collection(self, client, sample_collection):
        resp = client.delete(f"/api/collections/{sample_collection['id']}")
        assert resp.status_code == 200
        assert resp.get_json()["ok"] is True

    def test_filter_snippets_by_collection(self, client, sample_collection):
        client.post("/api/snippets", json={"title": "In", "collection_id": sample_collection["id"]})
        client.post("/api/snippets", json={"title": "Out"})
        resp = client.get(f"/api/snippets?collection_id={sample_collection['id']}")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "In"


class TestStatsAPI:
    """Tests for language statistics API."""

    def test_language_stats(self, client):
        client.post("/api/snippets", json={"title": "A", "language": "python", "code": "x"})
        client.post("/api/snippets", json={"title": "B", "language": "python", "code": "y"})
        client.post("/api/snippets", json={"title": "C", "language": "javascript", "code": "z"})
        resp = client.get("/api/stats/languages")
        data = resp.get_json()
        assert len(data) == 2
        py = next(s for s in data if s["language"] == "python")
        assert py["count"] == 2


class TestHealthAPI:
    """Tests for health endpoint."""

    def test_health(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"


class TestFrontend:
    """Tests for frontend HTML serving."""

    def test_root_serves_html(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"SnipStash" in resp.data
        assert resp.content_type == "text/html"

    def test_slug_route_serves_html(self, client):
        resp = client.get("/s/someslug")
        assert resp.status_code == 200
        assert b"SnipStash" in resp.data
