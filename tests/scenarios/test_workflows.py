"""Scenario tests for full user workflows."""

import pytest

pytestmark = pytest.mark.scenario


class TestFullSnippetLifecycle:
    """Test complete snippet create -> edit -> star -> fork -> delete workflow."""

    def test_create_edit_star_fork_delete(self, client):
        # 1. Create a snippet
        resp = client.post("/api/snippets", json={
            "title": "Original Snippet",
            "description": "My first snippet",
            "code": "def hello(): return 'world'",
            "language": "python",
            "filename": "hello.py",
            "tags": ["demo"],
            "visibility": "public",
        })
        assert resp.status_code == 201
        snippet = resp.get_json()
        sid = snippet["id"]

        # 2. Edit the snippet
        resp = client.put(f"/api/snippets/{sid}", json={
            "title": "Updated Snippet",
            "code": "def hello(): return 'universe'",
        })
        assert resp.status_code == 200
        assert resp.get_json()["title"] == "Updated Snippet"

        # 3. Verify version history
        resp = client.get(f"/api/snippets/{sid}/versions")
        versions = resp.get_json()
        assert len(versions) == 1
        assert versions[0]["title"] == "Original Snippet"

        # 4. Star the snippet
        resp = client.post(f"/api/snippets/{sid}/star")
        assert resp.get_json()["starred"] is True

        # 5. Verify it appears in starred list
        resp = client.get("/api/snippets?starred=1")
        starred = resp.get_json()
        assert len(starred) == 1
        assert starred[0]["id"] == sid

        # 6. Fork the snippet
        resp = client.post(f"/api/snippets/{sid}/fork")
        assert resp.status_code == 201
        forked = resp.get_json()
        assert forked["fork_of"] == sid
        assert forked["id"] != sid

        # 7. Verify both exist
        resp = client.get("/api/snippets")
        assert len(resp.get_json()) == 2

        # 8. Delete original
        resp = client.delete(f"/api/snippets/{sid}")
        assert resp.status_code == 200

        # 9. Fork still exists
        resp = client.get(f"/api/snippets/{forked['id']}")
        assert resp.status_code == 200

        # 10. Total is now 1
        resp = client.get("/api/snippets")
        assert len(resp.get_json()) == 1


class TestCollectionOrganization:
    """Test collection-based organization workflow."""

    def test_organize_snippets_into_collections(self, client):
        # 1. Create collections
        resp = client.post("/api/collections", json={"name": "Python Utils"})
        py_coll = resp.get_json()

        resp = client.post("/api/collections", json={"name": "JavaScript"})
        js_coll = resp.get_json()

        # 2. Create snippets in collections
        resp = client.post("/api/snippets", json={
            "title": "Python Logger",
            "code": "import logging",
            "language": "python",
            "collection_id": py_coll["id"],
        })
        py_snippet = resp.get_json()

        resp = client.post("/api/snippets", json={
            "title": "JS Fetch Wrapper",
            "code": "async function fetchJson(url) {}",
            "language": "javascript",
            "collection_id": js_coll["id"],
        })

        # 3. Filter by collection
        resp = client.get(f"/api/snippets?collection_id={py_coll['id']}")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "Python Logger"

        # 4. Move snippet to different collection
        resp = client.put(f"/api/snippets/{py_snippet['id']}", json={
            "collection_id": js_coll["id"],
        })
        assert resp.status_code == 200

        # 5. Verify move
        resp = client.get(f"/api/snippets?collection_id={py_coll['id']}")
        assert len(resp.get_json()) == 0

        resp = client.get(f"/api/snippets?collection_id={js_coll['id']}")
        assert len(resp.get_json()) == 2

        # 6. Delete collection - snippets should remain
        resp = client.delete(f"/api/collections/{js_coll['id']}")
        assert resp.status_code == 200

        resp = client.get("/api/snippets")
        assert len(resp.get_json()) == 2


class TestSearchWorkflow:
    """Test search and discovery workflow."""

    def test_search_across_content(self, client):
        # Create diverse snippets
        client.post("/api/snippets", json={
            "title": "Flask API",
            "description": "REST API with Flask",
            "code": "from flask import Flask\napp = Flask(__name__)",
            "language": "python",
            "tags": ["web", "api"],
        })
        client.post("/api/snippets", json={
            "title": "React Component",
            "description": "Simple React button",
            "code": "function Button({ label }) { return <button>{label}</button>; }",
            "language": "javascript",
            "tags": ["frontend", "react"],
        })
        client.post("/api/snippets", json={
            "title": "Docker Compose",
            "description": "PostgreSQL setup",
            "code": "services:\n  db:\n    image: postgres",
            "language": "yaml",
            "tags": ["devops", "docker"],
        })

        # Search by title
        resp = client.get("/api/snippets/search?q=flask")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "Flask API"

        # Search by code content
        resp = client.get("/api/snippets/search?q=postgres")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "Docker Compose"

        # Search by tag
        resp = client.get("/api/snippets/search?q=react")
        data = resp.get_json()
        assert len(data) >= 1

        # Language stats
        resp = client.get("/api/stats/languages")
        stats = resp.get_json()
        assert len(stats) == 3


class TestShareableLinks:
    """Test shareable link workflow."""

    def test_share_via_slug(self, client):
        # Create snippet
        resp = client.post("/api/snippets", json={
            "title": "Shared Code",
            "code": "print('share me')",
            "language": "python",
            "visibility": "public",
        })
        snippet = resp.get_json()
        slug = snippet["slug"]

        # Access via slug
        resp = client.get(f"/api/snippets/slug/{slug}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["title"] == "Shared Code"

        # Frontend route for shared link
        resp = client.get(f"/s/{slug}")
        assert resp.status_code == 200
        assert b"SnipStash" in resp.data


class TestMultiFileSnippet:
    """Test multi-file snippet workflow."""

    def test_create_and_view_multifile(self, client):
        # Create multi-file snippet
        resp = client.post("/api/snippets", json={
            "title": "Flask Project",
            "description": "A complete Flask app",
            "files": [
                {"filename": "app.py", "code": "from flask import Flask", "language": "python"},
                {"filename": "requirements.txt", "code": "flask==3.0", "language": "text"},
                {"filename": "Dockerfile", "code": "FROM python:3.12", "language": "text"},
            ],
            "tags": ["flask", "docker"],
        })
        assert resp.status_code == 201
        snippet = resp.get_json()
        assert len(snippet["files"]) == 3

        # Retrieve and verify files
        resp = client.get(f"/api/snippets/{snippet['id']}")
        data = resp.get_json()
        assert data["files"][0]["filename"] == "app.py"
        assert data["files"][1]["filename"] == "requirements.txt"
        assert data["files"][2]["filename"] == "Dockerfile"

        # Edit: add a file
        resp = client.put(f"/api/snippets/{snippet['id']}", json={
            "files": [
                {"filename": "app.py", "code": "from flask import Flask\napp = Flask(__name__)", "language": "python"},
                {"filename": "requirements.txt", "code": "flask==3.1.0", "language": "text"},
                {"filename": "Dockerfile", "code": "FROM python:3.12", "language": "text"},
                {"filename": "docker-compose.yml", "code": "services:\n  web:\n    build: .", "language": "yaml"},
            ],
        })
        assert resp.status_code == 200
        assert len(resp.get_json()["files"]) == 4

        # Verify version was created
        resp = client.get(f"/api/snippets/{snippet['id']}/versions")
        assert len(resp.get_json()) == 1
