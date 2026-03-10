"""Unit tests for the in-memory store module."""

from api import store


class TestCreateSnippet:
    """Tests for snippet creation."""

    def test_create_snippet_basic(self):
        s = store.create_snippet({
            "title": "Test",
            "code": "print('hello')",
            "language": "python",
        })
        assert s["title"] == "Test"
        assert s["id"] is not None
        assert s["slug"] is not None
        assert len(s["files"]) == 1
        assert s["files"][0]["code"] == "print('hello')"
        assert s["files"][0]["language"] == "python"

    def test_create_snippet_defaults(self):
        s = store.create_snippet({})
        assert s["title"] == "Untitled"
        assert s["visibility"] == "public"
        assert s["tags"] == []
        assert s["description"] == ""

    def test_create_snippet_with_tags(self):
        s = store.create_snippet({"title": "Tagged", "tags": ["api", "utils"]})
        assert s["tags"] == ["api", "utils"]

    def test_create_snippet_private(self):
        s = store.create_snippet({"title": "Secret", "visibility": "private"})
        assert s["visibility"] == "private"

    def test_create_snippet_multifile(self):
        s = store.create_snippet({
            "title": "Multi",
            "files": [
                {"filename": "main.py", "code": "import lib", "language": "python"},
                {"filename": "lib.py", "code": "def helper(): pass", "language": "python"},
            ],
        })
        assert len(s["files"]) == 2
        assert s["files"][0]["filename"] == "main.py"
        assert s["files"][1]["filename"] == "lib.py"


class TestGetSnippet:
    """Tests for snippet retrieval."""

    def test_get_existing_snippet(self):
        created = store.create_snippet({"title": "Find me"})
        found = store.get_snippet(created["id"])
        assert found is not None
        assert found["title"] == "Find me"

    def test_get_nonexistent_snippet(self):
        assert store.get_snippet("nonexistent") is None

    def test_get_by_slug(self):
        created = store.create_snippet({"title": "Sluggy"})
        found = store.get_snippet_by_slug(created["slug"])
        assert found is not None
        assert found["title"] == "Sluggy"

    def test_get_by_slug_nonexistent(self):
        assert store.get_snippet_by_slug("nosuchslug") is None


class TestUpdateSnippet:
    """Tests for snippet updates."""

    def test_update_title(self):
        s = store.create_snippet({"title": "Old"})
        updated = store.update_snippet(s["id"], {"title": "New"})
        assert updated["title"] == "New"

    def test_update_creates_version(self):
        s = store.create_snippet({"title": "V1", "code": "x = 1"})
        store.update_snippet(s["id"], {"title": "V2", "code": "x = 2"})
        result = store.get_snippet(s["id"])
        assert len(result["versions"]) == 1
        assert result["versions"][0]["title"] == "V1"

    def test_update_nonexistent(self):
        assert store.update_snippet("nope", {"title": "X"}) is None

    def test_update_tags(self):
        s = store.create_snippet({"title": "T", "tags": ["a"]})
        updated = store.update_snippet(s["id"], {"tags": ["b", "c"]})
        assert updated["tags"] == ["b", "c"]

    def test_update_visibility(self):
        s = store.create_snippet({"title": "T", "visibility": "public"})
        updated = store.update_snippet(s["id"], {"visibility": "private"})
        assert updated["visibility"] == "private"


class TestDeleteSnippet:
    """Tests for snippet deletion."""

    def test_delete_existing(self):
        s = store.create_snippet({"title": "Delete me"})
        assert store.delete_snippet(s["id"]) is True
        assert store.get_snippet(s["id"]) is None

    def test_delete_nonexistent(self):
        assert store.delete_snippet("nope") is False


class TestListSnippets:
    """Tests for listing snippets."""

    def test_list_empty(self):
        assert store.list_snippets() == []

    def test_list_all(self):
        store.create_snippet({"title": "A"})
        store.create_snippet({"title": "B"})
        assert len(store.list_snippets()) == 2

    def test_filter_by_visibility(self):
        store.create_snippet({"title": "Pub", "visibility": "public"})
        store.create_snippet({"title": "Priv", "visibility": "private"})
        pubs = store.list_snippets({"visibility": "public"})
        assert len(pubs) == 1
        assert pubs[0]["title"] == "Pub"

    def test_filter_by_language(self):
        store.create_snippet({"title": "Py", "code": "pass", "language": "python"})
        store.create_snippet({"title": "JS", "code": "1", "language": "javascript"})
        py = store.list_snippets({"language": "python"})
        assert len(py) == 1
        assert py[0]["title"] == "Py"

    def test_filter_by_tag(self):
        store.create_snippet({"title": "Tagged", "tags": ["api"]})
        store.create_snippet({"title": "Untagged"})
        tagged = store.list_snippets({"tag": "api"})
        assert len(tagged) == 1
        assert tagged[0]["title"] == "Tagged"


class TestStarSnippet:
    """Tests for starring snippets."""

    def test_star_toggle(self):
        s = store.create_snippet({"title": "Star me"})
        assert store.toggle_star(s["id"]) is True  # starred
        assert store.toggle_star(s["id"]) is False  # unstarred

    def test_star_nonexistent(self):
        assert store.toggle_star("nope") is None

    def test_starred_filter(self):
        s = store.create_snippet({"title": "Starred"})
        store.create_snippet({"title": "Not starred"})
        store.toggle_star(s["id"])
        starred = store.list_snippets({"starred": True})
        assert len(starred) == 1
        assert starred[0]["title"] == "Starred"


class TestForkSnippet:
    """Tests for forking snippets."""

    def test_fork_creates_copy(self):
        original = store.create_snippet({"title": "Original", "code": "x=1", "tags": ["a"]})
        forked = store.fork_snippet(original["id"])
        assert forked is not None
        assert forked["id"] != original["id"]
        assert forked["title"] == "Original (fork)"
        assert forked["fork_of"] == original["id"]
        assert forked["visibility"] == "private"
        assert forked["files"][0]["code"] == "x=1"

    def test_fork_nonexistent(self):
        assert store.fork_snippet("nope") is None


class TestSearchSnippets:
    """Tests for search functionality."""

    def test_search_by_title(self):
        store.create_snippet({"title": "Flask API Guide"})
        store.create_snippet({"title": "React Tutorial"})
        results = store.search_snippets("flask")
        assert len(results) == 1
        assert results[0]["title"] == "Flask API Guide"

    def test_search_by_code(self):
        store.create_snippet({"title": "Demo", "code": "def fibonacci(n): pass"})
        results = store.search_snippets("fibonacci")
        assert len(results) == 1

    def test_search_by_tag(self):
        store.create_snippet({"title": "T", "tags": ["algorithm"]})
        results = store.search_snippets("algorithm")
        assert len(results) == 1

    def test_search_empty_query(self):
        store.create_snippet({"title": "X"})
        results = store.search_snippets("")
        assert len(results) == 1


class TestCollections:
    """Tests for collection operations."""

    def test_create_collection(self):
        c = store.create_collection({"name": "Python"})
        assert c["name"] == "Python"
        assert c["id"] is not None

    def test_list_collections(self):
        store.create_collection({"name": "B"})
        store.create_collection({"name": "A"})
        colls = store.list_collections()
        assert len(colls) == 2
        assert colls[0]["name"] == "A"  # sorted

    def test_update_collection(self):
        c = store.create_collection({"name": "Old"})
        updated = store.update_collection(c["id"], {"name": "New"})
        assert updated["name"] == "New"

    def test_delete_collection_unlinks_snippets(self):
        c = store.create_collection({"name": "C"})
        s = store.create_snippet({"title": "S", "collection_id": c["id"]})
        store.delete_collection(c["id"])
        snippet = store.get_snippet(s["id"])
        assert snippet["collection_id"] is None

    def test_filter_by_collection(self):
        c = store.create_collection({"name": "C"})
        store.create_snippet({"title": "In", "collection_id": c["id"]})
        store.create_snippet({"title": "Out"})
        in_coll = store.list_snippets({"collection_id": c["id"]})
        assert len(in_coll) == 1
        assert in_coll[0]["title"] == "In"


class TestLanguageDetection:
    """Tests for language auto-detection."""

    def test_detect_from_filename(self):
        assert store._detect_language("", "main.py") == "python"
        assert store._detect_language("", "app.js") == "javascript"
        assert store._detect_language("", "main.go") == "go"
        assert store._detect_language("", "lib.rs") == "rust"
        assert store._detect_language("", "index.html") == "html"
        assert store._detect_language("", "style.css") == "css"

    def test_detect_from_code_python(self):
        assert store._detect_language("def hello():\n    print('hi')") == "python"

    def test_detect_from_code_javascript(self):
        assert store._detect_language("const x = () => console.log('hi')") == "javascript"

    def test_detect_from_code_html(self):
        assert store._detect_language("<!DOCTYPE html>") == "html"

    def test_detect_fallback(self):
        assert store._detect_language("random text here") == "text"
        assert store._detect_language("") == "text"


class TestLanguageStats:
    """Tests for language statistics."""

    def test_empty_stats(self):
        assert store.language_stats() == []

    def test_counts_per_language(self):
        store.create_snippet({"title": "A", "code": "x", "language": "python"})
        store.create_snippet({"title": "B", "code": "y", "language": "python"})
        store.create_snippet({"title": "C", "code": "z", "language": "javascript"})
        stats = store.language_stats()
        py = next(s for s in stats if s["language"] == "python")
        js = next(s for s in stats if s["language"] == "javascript")
        assert py["count"] == 2
        assert js["count"] == 1
        assert stats[0]["language"] == "python"  # sorted by count desc


class TestVersioning:
    """Tests for snippet versioning."""

    def test_version_created_on_update(self):
        s = store.create_snippet({"title": "V1", "code": "v1"})
        store.update_snippet(s["id"], {"title": "V2", "code": "v2"})
        result = store.get_snippet(s["id"])
        assert len(result["versions"]) == 1
        assert result["versions"][0]["version"] == 1
        assert result["versions"][0]["title"] == "V1"

    def test_multiple_versions(self):
        s = store.create_snippet({"title": "V1", "code": "v1"})
        store.update_snippet(s["id"], {"title": "V2"})
        store.update_snippet(s["id"], {"title": "V3"})
        result = store.get_snippet(s["id"])
        assert len(result["versions"]) == 2
        assert result["versions"][0]["version"] == 1
        assert result["versions"][1]["version"] == 2


class TestReset:
    """Tests for store reset."""

    def test_reset_clears_all(self):
        store.create_snippet({"title": "T"})
        store.create_collection({"name": "C"})
        store.reset()
        assert store.list_snippets() == []
        assert store.list_collections() == []
