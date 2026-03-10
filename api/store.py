"""In-memory data store for snippets, collections, and related entities."""

import uuid
import copy
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc).isoformat()


def _gen_id():
    return uuid.uuid4().hex[:12]


def _gen_slug():
    return uuid.uuid4().hex[:8]


# ── In-memory storage ────────────────────────────────────────────────
snippets = {}       # id -> snippet dict
collections = {}    # id -> collection dict
stars = set()       # set of snippet ids


def reset():
    """Clear all data. Used by tests."""
    snippets.clear()
    collections.clear()
    stars.clear()


# ── Language colors ──────────────────────────────────────────────────
LANGUAGE_COLORS = {
    "javascript": "#f1e05a",
    "python": "#3572A5",
    "go": "#00ADD8",
    "rust": "#dea584",
    "html": "#e34c26",
    "css": "#563d7c",
    "typescript": "#3178c6",
    "ruby": "#701516",
    "java": "#b07219",
    "c": "#555555",
    "cpp": "#f34b7d",
    "shell": "#89e051",
    "markdown": "#083fa1",
    "json": "#292929",
    "yaml": "#cb171e",
    "sql": "#e38c00",
    "php": "#4F5D95",
    "swift": "#F05138",
    "kotlin": "#A97BFF",
    "text": "#888888",
}


def _detect_language(code, filename=None):
    """Auto-detect language from filename extension or code content."""
    if filename:
        ext_map = {
            ".py": "python", ".js": "javascript", ".ts": "typescript",
            ".go": "go", ".rs": "rust", ".html": "html", ".htm": "html",
            ".css": "css", ".rb": "ruby", ".java": "java", ".c": "c",
            ".cpp": "cpp", ".cc": "cpp", ".h": "c", ".hpp": "cpp",
            ".sh": "shell", ".bash": "shell", ".zsh": "shell",
            ".md": "markdown", ".json": "json", ".yaml": "yaml",
            ".yml": "yaml", ".sql": "sql", ".php": "php",
            ".swift": "swift", ".kt": "kotlin", ".txt": "text",
        }
        for ext, lang in ext_map.items():
            if filename.lower().endswith(ext):
                return lang

    if not code:
        return "text"

    # Heuristic detection from code content
    code_lower = code.strip().lower()
    if code_lower.startswith("<!doctype") or code_lower.startswith("<html"):
        return "html"
    if "def " in code and ("import " in code or "print(" in code or "self." in code):
        return "python"
    if "func " in code and ("package " in code or "fmt." in code):
        return "go"
    if ("fn " in code or "let mut " in code) and ("::" in code or "-> " in code):
        return "rust"
    if "function " in code or "const " in code or "=>" in code or "console.log" in code:
        return "javascript"
    if "{" in code and "}" in code and ("color:" in code or "margin:" in code or "display:" in code):
        return "css"

    return "text"


# ── Snippet CRUD ─────────────────────────────────────────────────────

def create_snippet(data):
    """Create a new snippet. Returns the created snippet dict."""
    sid = _gen_id()
    slug = _gen_slug()
    now = _now()

    # Handle multi-file: if files provided, use them; otherwise create single file
    files = data.get("files", [])
    if not files:
        code = data.get("code", "")
        filename = data.get("filename", "main")
        lang = data.get("language", "") or _detect_language(code, filename)
        files = [{"filename": filename, "code": code, "language": lang}]
    else:
        for f in files:
            if not f.get("language"):
                f["language"] = _detect_language(f.get("code", ""), f.get("filename"))

    snippet = {
        "id": sid,
        "slug": slug,
        "title": data.get("title", "Untitled"),
        "description": data.get("description", ""),
        "files": files,
        "tags": data.get("tags", []),
        "visibility": data.get("visibility", "public"),
        "starred": False,
        "fork_of": data.get("fork_of"),
        "versions": [],
        "collection_id": data.get("collection_id"),
        "created_at": now,
        "updated_at": now,
    }

    snippets[sid] = snippet
    return copy.deepcopy(snippet)


def get_snippet(sid):
    """Get a snippet by ID. Returns None if not found."""
    s = snippets.get(sid)
    if s:
        s = copy.deepcopy(s)
        s["starred"] = sid in stars
    return s


def get_snippet_by_slug(slug):
    """Get a snippet by its slug. Returns None if not found."""
    for s in snippets.values():
        if s["slug"] == slug:
            result = copy.deepcopy(s)
            result["starred"] = s["id"] in stars
            return result
    return None


def list_snippets(filters=None):
    """List all snippets with optional filters."""
    result = []
    filters = filters or {}

    for s in snippets.values():
        # Apply filters
        if filters.get("visibility") and s["visibility"] != filters["visibility"]:
            continue
        if filters.get("language"):
            langs = [f["language"] for f in s["files"]]
            if filters["language"] not in langs:
                continue
        if filters.get("tag"):
            if filters["tag"] not in s.get("tags", []):
                continue
        if filters.get("collection_id"):
            if s.get("collection_id") != filters["collection_id"]:
                continue
        if filters.get("starred"):
            if s["id"] not in stars:
                continue

        item = copy.deepcopy(s)
        item["starred"] = s["id"] in stars
        result.append(item)

    # Sort by updated_at descending
    result.sort(key=lambda x: x["updated_at"], reverse=True)
    return result


def update_snippet(sid, data):
    """Update an existing snippet. Creates a version entry. Returns updated snippet or None."""
    s = snippets.get(sid)
    if not s:
        return None

    # Save version before update
    version = {
        "version": len(s["versions"]) + 1,
        "files": copy.deepcopy(s["files"]),
        "title": s["title"],
        "description": s["description"],
        "updated_at": s["updated_at"],
    }
    s["versions"].append(version)

    # Apply updates
    if "title" in data:
        s["title"] = data["title"]
    if "description" in data:
        s["description"] = data["description"]
    if "tags" in data:
        s["tags"] = data["tags"]
    if "visibility" in data:
        s["visibility"] = data["visibility"]
    if "collection_id" in data:
        s["collection_id"] = data["collection_id"]

    # Update files
    if "files" in data:
        for f in data["files"]:
            if not f.get("language"):
                f["language"] = _detect_language(f.get("code", ""), f.get("filename"))
        s["files"] = data["files"]
    elif "code" in data:
        lang = data.get("language", "") or _detect_language(data["code"], s["files"][0].get("filename"))
        s["files"] = [{"filename": s["files"][0].get("filename", "main"), "code": data["code"], "language": lang}]

    s["updated_at"] = _now()
    result = copy.deepcopy(s)
    result["starred"] = sid in stars
    return result


def delete_snippet(sid):
    """Delete a snippet by ID. Returns True if deleted, False if not found."""
    if sid in snippets:
        del snippets[sid]
        stars.discard(sid)
        return True
    return False


# ── Stars ────────────────────────────────────────────────────────────

def toggle_star(sid):
    """Toggle star status. Returns new starred state."""
    if sid not in snippets:
        return None
    if sid in stars:
        stars.discard(sid)
        return False
    else:
        stars.add(sid)
        return True


# ── Fork ─────────────────────────────────────────────────────────────

def fork_snippet(sid):
    """Fork a snippet, creating an independent copy."""
    original = snippets.get(sid)
    if not original:
        return None
    data = {
        "title": f"{original['title']} (fork)",
        "description": original["description"],
        "files": copy.deepcopy(original["files"]),
        "tags": list(original["tags"]),
        "visibility": "private",
        "fork_of": sid,
    }
    return create_snippet(data)


# ── Collections ──────────────────────────────────────────────────────

def create_collection(data):
    """Create a new collection."""
    cid = _gen_id()
    now = _now()
    collection = {
        "id": cid,
        "name": data.get("name", "Untitled Collection"),
        "description": data.get("description", ""),
        "parent_id": data.get("parent_id"),
        "created_at": now,
        "updated_at": now,
    }
    collections[cid] = collection
    return copy.deepcopy(collection)


def get_collection(cid):
    """Get a collection by ID."""
    c = collections.get(cid)
    return copy.deepcopy(c) if c else None


def list_collections():
    """List all collections."""
    result = [copy.deepcopy(c) for c in collections.values()]
    result.sort(key=lambda x: x["name"])
    return result


def update_collection(cid, data):
    """Update a collection. Returns updated collection or None."""
    c = collections.get(cid)
    if not c:
        return None
    if "name" in data:
        c["name"] = data["name"]
    if "description" in data:
        c["description"] = data["description"]
    c["updated_at"] = _now()
    return copy.deepcopy(c)


def delete_collection(cid):
    """Delete a collection. Unlinks snippets but doesn't delete them."""
    if cid not in collections:
        return False
    # Unlink snippets
    for s in snippets.values():
        if s.get("collection_id") == cid:
            s["collection_id"] = None
    del collections[cid]
    return True


# ── Search ───────────────────────────────────────────────────────────

def search_snippets(query):
    """Full-text search across title, description, and code content."""
    if not query:
        return list_snippets()

    query_lower = query.lower()
    results = []

    for s in snippets.values():
        score = 0
        # Title match (highest weight)
        if query_lower in s["title"].lower():
            score += 3
        # Description match
        if query_lower in s.get("description", "").lower():
            score += 2
        # Code match
        for f in s["files"]:
            if query_lower in f.get("code", "").lower():
                score += 1
                break
        # Tag match
        for tag in s.get("tags", []):
            if query_lower in tag.lower():
                score += 2
                break

        if score > 0:
            item = copy.deepcopy(s)
            item["starred"] = s["id"] in stars
            item["_score"] = score
            results.append(item)

    results.sort(key=lambda x: (-x["_score"], x["updated_at"]))
    # Remove internal score field
    for r in results:
        r.pop("_score", None)
    return results


# ── Language Stats ───────────────────────────────────────────────────

def language_stats():
    """Get snippet count per language."""
    stats = {}
    for s in snippets.values():
        for f in s["files"]:
            lang = f.get("language", "text")
            stats[lang] = stats.get(lang, 0) + 1

    result = [
        {"language": lang, "count": count, "color": LANGUAGE_COLORS.get(lang, "#888888")}
        for lang, count in stats.items()
    ]
    result.sort(key=lambda x: -x["count"])
    return result
