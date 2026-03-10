"""Flask application with API routes and HTML frontend."""

from flask import Flask, request, jsonify, Response
from api import store


def create_app():
    app = Flask(__name__)

    # ── API Routes ───────────────────────────────────────────────────

    @app.route("/api/snippets", methods=["GET"])
    def api_list_snippets():
        filters = {}
        if request.args.get("visibility"):
            filters["visibility"] = request.args["visibility"]
        if request.args.get("language"):
            filters["language"] = request.args["language"]
        if request.args.get("tag"):
            filters["tag"] = request.args["tag"]
        if request.args.get("collection_id"):
            filters["collection_id"] = request.args["collection_id"]
        if request.args.get("starred"):
            filters["starred"] = True
        return jsonify(store.list_snippets(filters))

    @app.route("/api/snippets", methods=["POST"])
    def api_create_snippet():
        data = request.get_json(force=True)
        snippet = store.create_snippet(data)
        return jsonify(snippet), 201

    @app.route("/api/snippets/<sid>", methods=["GET"])
    def api_get_snippet(sid):
        snippet = store.get_snippet(sid)
        if not snippet:
            return jsonify({"error": "Snippet not found"}), 404
        return jsonify(snippet)

    @app.route("/api/snippets/<sid>", methods=["PUT"])
    def api_update_snippet(sid):
        data = request.get_json(force=True)
        snippet = store.update_snippet(sid, data)
        if not snippet:
            return jsonify({"error": "Snippet not found"}), 404
        return jsonify(snippet)

    @app.route("/api/snippets/<sid>", methods=["DELETE"])
    def api_delete_snippet(sid):
        if store.delete_snippet(sid):
            return jsonify({"ok": True})
        return jsonify({"error": "Snippet not found"}), 404

    @app.route("/api/snippets/<sid>/star", methods=["POST"])
    def api_toggle_star(sid):
        result = store.toggle_star(sid)
        if result is None:
            return jsonify({"error": "Snippet not found"}), 404
        return jsonify({"starred": result})

    @app.route("/api/snippets/<sid>/fork", methods=["POST"])
    def api_fork_snippet(sid):
        forked = store.fork_snippet(sid)
        if not forked:
            return jsonify({"error": "Snippet not found"}), 404
        return jsonify(forked), 201

    @app.route("/api/snippets/<sid>/versions", methods=["GET"])
    def api_snippet_versions(sid):
        snippet = store.get_snippet(sid)
        if not snippet:
            return jsonify({"error": "Snippet not found"}), 404
        return jsonify(snippet.get("versions", []))

    @app.route("/api/snippets/search", methods=["GET"])
    def api_search_snippets():
        query = request.args.get("q", "")
        return jsonify(store.search_snippets(query))

    @app.route("/api/snippets/slug/<slug>", methods=["GET"])
    def api_get_by_slug(slug):
        snippet = store.get_snippet_by_slug(slug)
        if not snippet:
            return jsonify({"error": "Snippet not found"}), 404
        return jsonify(snippet)

    # ── Collections ──────────────────────────────────────────────────

    @app.route("/api/collections", methods=["GET"])
    def api_list_collections():
        return jsonify(store.list_collections())

    @app.route("/api/collections", methods=["POST"])
    def api_create_collection():
        data = request.get_json(force=True)
        collection = store.create_collection(data)
        return jsonify(collection), 201

    @app.route("/api/collections/<cid>", methods=["GET"])
    def api_get_collection(cid):
        collection = store.get_collection(cid)
        if not collection:
            return jsonify({"error": "Collection not found"}), 404
        return jsonify(collection)

    @app.route("/api/collections/<cid>", methods=["PUT"])
    def api_update_collection(cid):
        data = request.get_json(force=True)
        collection = store.update_collection(cid, data)
        if not collection:
            return jsonify({"error": "Collection not found"}), 404
        return jsonify(collection)

    @app.route("/api/collections/<cid>", methods=["DELETE"])
    def api_delete_collection(cid):
        if store.delete_collection(cid):
            return jsonify({"ok": True})
        return jsonify({"error": "Collection not found"}), 404

    # ── Stats ────────────────────────────────────────────────────────

    @app.route("/api/stats/languages", methods=["GET"])
    def api_language_stats():
        return jsonify(store.language_stats())

    # ── Health ───────────────────────────────────────────────────────

    @app.route("/api/health", methods=["GET"])
    def api_health():
        return jsonify({"status": "ok", "snippets": len(store.snippets)})

    # ── Frontend ─────────────────────────────────────────────────────

    @app.route("/", methods=["GET"])
    @app.route("/s/<slug>", methods=["GET"])
    def serve_frontend(slug=None):
        return Response(FRONTEND_HTML, content_type="text/html")

    return app


# ── Frontend HTML ────────────────────────────────────────────────────
# Embedded as a string constant so Vercel can serve it without static files.

FRONTEND_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SnipStash — Code Snippet Manager</title>
<style>
/* ── Reset & Base ──────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg-primary: #1e1e2e;
  --bg-secondary: #272838;
  --bg-card: #2a2a3c;
  --bg-card-hover: #313145;
  --bg-input: #1a1a2e;
  --bg-sidebar: #1a1a2e;
  --text-primary: #e0e0e0;
  --text-secondary: #a0a0b0;
  --text-muted: #666680;
  --accent-green: #a6e22e;
  --accent-pink: #f92672;
  --accent-yellow: #e6db74;
  --accent-blue: #66d9ef;
  --accent-orange: #fd971f;
  --accent-purple: #ae81ff;
  --border-color: #3a3a50;
  --shadow-card: 0 2px 8px rgba(0,0,0,0.3);
  --shadow-card-hover: 0 8px 24px rgba(0,0,0,0.5);
  --radius: 8px;
  --radius-lg: 12px;
  --transition: 0.2s ease;
  --font-mono: 'SF Mono', 'Fira Code', 'JetBrains Mono', 'Cascadia Code', Consolas, monospace;
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

body {
  font-family: var(--font-sans);
  background: var(--bg-primary);
  color: var(--text-primary);
  min-height: 100vh;
  line-height: 1.5;
}

/* ── Layout ───────────────────────────────────────────── */
.app-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 260px;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border-color);
  padding: 20px 0;
  flex-shrink: 0;
  overflow-y: auto;
  position: sticky;
  top: 0;
  height: 100vh;
}

.main-content {
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
  min-height: 100vh;
}

/* ── Sidebar ──────────────────────────────────────────── */
.sidebar-brand {
  padding: 0 20px 20px;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 16px;
}

.sidebar-brand h1 {
  font-size: 20px;
  font-weight: 700;
  color: var(--accent-green);
  letter-spacing: -0.5px;
}

.sidebar-brand p {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

.sidebar-nav {
  padding: 0 12px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 13px;
  transition: all var(--transition);
  border: none;
  background: none;
  width: 100%;
  text-align: left;
}

.nav-item:hover { background: var(--bg-card); color: var(--text-primary); }
.nav-item.active { background: var(--bg-card); color: var(--accent-green); }
.nav-item .nav-icon { font-size: 16px; width: 20px; text-align: center; }
.nav-item .nav-count {
  margin-left: auto;
  font-size: 11px;
  background: var(--bg-card);
  padding: 1px 6px;
  border-radius: 10px;
  color: var(--text-muted);
}

.sidebar-section {
  margin-top: 20px;
  padding: 0 12px;
}

.sidebar-section-title {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-muted);
  padding: 0 12px 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-section-title button {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 14px;
  padding: 0;
  line-height: 1;
}

.sidebar-section-title button:hover { color: var(--accent-green); }

.collection-tree { list-style: none; }
.collection-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 13px;
  transition: all var(--transition);
}
.collection-item:hover { background: var(--bg-card); color: var(--text-primary); }
.collection-item.active { color: var(--accent-blue); }
.collection-item .coll-icon { font-size: 14px; }

/* ── Language Stats ───────────────────────────────────── */
.lang-stats {
  padding: 0 12px;
  margin-top: 20px;
}

.lang-bar {
  display: flex;
  height: 6px;
  border-radius: 3px;
  overflow: hidden;
  margin: 8px 12px;
  gap: 1px;
}

.lang-bar-segment {
  height: 100%;
  transition: width var(--transition);
  min-width: 3px;
}

.lang-legend {
  padding: 0 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.lang-legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--text-muted);
}

.lang-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

/* ── Header Bar ───────────────────────────────────────── */
.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 480px;
}

.search-box input {
  width: 100%;
  padding: 10px 14px 10px 38px;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  transition: border-color var(--transition);
}

.search-box input:focus { border-color: var(--accent-blue); }
.search-box input::placeholder { color: var(--text-muted); }

.search-box .search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  font-size: 14px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: var(--radius);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition);
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-primary {
  background: var(--accent-green);
  color: #1e1e2e;
}
.btn-primary:hover { background: #b8f036; transform: translateY(-1px); }

.btn-secondary {
  background: var(--bg-card);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}
.btn-secondary:hover { background: var(--bg-card-hover); }

.btn-danger {
  background: transparent;
  color: var(--accent-pink);
  border: 1px solid var(--accent-pink);
}
.btn-danger:hover { background: var(--accent-pink); color: white; }

.btn-icon {
  padding: 8px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 16px;
  transition: all var(--transition);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.btn-icon:hover { background: var(--bg-card); color: var(--text-primary); }
.btn-icon.starred { color: var(--accent-yellow); border-color: var(--accent-yellow); }

/* ── Snippet Grid ─────────────────────────────────────── */
.snippet-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 16px;
}

.snippet-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all 0.25s ease;
  cursor: pointer;
}

.snippet-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-card-hover);
  border-color: var(--accent-blue);
}

.card-header {
  padding: 16px 16px 8px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-badges {
  display: flex;
  gap: 6px;
  align-items: center;
  margin-left: 8px;
  flex-shrink: 0;
}

.lang-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--text-muted);
  padding: 2px 8px;
  background: var(--bg-primary);
  border-radius: 10px;
}

.lang-badge .lang-dot { width: 6px; height: 6px; }

.visibility-badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.visibility-badge.public { background: rgba(166,226,46,0.15); color: var(--accent-green); }
.visibility-badge.private { background: rgba(249,38,114,0.15); color: var(--accent-pink); }

.card-desc {
  padding: 0 16px;
  font-size: 12px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-code {
  margin: 10px 16px;
  background: var(--bg-primary);
  border-radius: 6px;
  overflow: hidden;
  max-height: 120px;
  position: relative;
}

.card-code::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 30px;
  background: linear-gradient(transparent, var(--bg-primary));
  pointer-events: none;
}

.card-code pre {
  margin: 0;
  padding: 10px 12px;
  font-family: var(--font-mono);
  font-size: 12px;
  line-height: 1.5;
  overflow: hidden;
  white-space: pre;
  tab-size: 2;
}

.card-footer {
  padding: 10px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border-color);
}

.card-tags { display: flex; gap: 4px; flex-wrap: wrap; flex: 1; overflow: hidden; }

.tag-chip {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 10px;
  white-space: nowrap;
}

.card-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.card-actions button {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 14px;
  padding: 4px;
  border-radius: 4px;
  transition: all var(--transition);
}

.card-actions button:hover { color: var(--text-primary); background: var(--bg-primary); }
.card-actions button.starred { color: var(--accent-yellow); }

.card-meta {
  font-size: 11px;
  color: var(--text-muted);
}

/* ── Copy button ──────────────────────────────────────── */
.copy-btn {
  position: relative;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 4px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all var(--transition);
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.copy-btn:hover { background: var(--bg-card-hover); color: var(--text-primary); }
.copy-btn.copied { color: var(--accent-green); border-color: var(--accent-green); }
.copy-btn .check { display: none; }
.copy-btn.copied .check { display: inline; }
.copy-btn.copied .copy-icon { display: none; }

/* ── Modal / Editor ───────────────────────────────────── */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease;
}

.modal-overlay.active { opacity: 1; pointer-events: all; }

.modal {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  transform: translateY(20px);
  transition: transform 0.2s ease;
}

.modal-overlay.active .modal { transform: translateY(0); }

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  font-size: 18px;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 20px;
  cursor: pointer;
  padding: 4px;
}
.modal-close:hover { color: var(--text-primary); }

.modal-body { padding: 24px; }

.form-group { margin-bottom: 16px; }
.form-group label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-group input, .form-group select {
  width: 100%;
  padding: 10px 14px;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
}

.form-group input:focus, .form-group select:focus { border-color: var(--accent-blue); }

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

/* ── Code Editor ──────────────────────────────────────── */
.code-editor-wrap {
  position: relative;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  overflow: hidden;
}

.code-editor-wrap:focus-within { border-color: var(--accent-blue); }

.file-tabs {
  display: flex;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  overflow-x: auto;
}

.file-tab {
  padding: 8px 16px;
  font-size: 12px;
  font-family: var(--font-mono);
  color: var(--text-muted);
  cursor: pointer;
  border: none;
  background: none;
  border-bottom: 2px solid transparent;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all var(--transition);
}

.file-tab:hover { color: var(--text-primary); background: var(--bg-card); }
.file-tab.active { color: var(--text-primary); border-bottom-color: var(--accent-blue); background: var(--bg-input); }

.file-tab .tab-close {
  font-size: 14px;
  line-height: 1;
  opacity: 0;
  transition: opacity var(--transition);
}

.file-tab:hover .tab-close { opacity: 1; }
.file-tab .tab-close:hover { color: var(--accent-pink); }

.add-file-tab {
  padding: 8px 12px;
  font-size: 14px;
  color: var(--text-muted);
  cursor: pointer;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
}
.add-file-tab:hover { color: var(--accent-green); }

.editor-container {
  display: flex;
  min-height: 200px;
  max-height: 400px;
}

.line-numbers {
  padding: 12px 0;
  min-width: 40px;
  text-align: right;
  font-family: var(--font-mono);
  font-size: 12px;
  line-height: 1.5;
  color: var(--text-muted);
  user-select: none;
  overflow: hidden;
  padding-right: 8px;
  background: rgba(0,0,0,0.1);
}

.code-textarea {
  flex: 1;
  padding: 12px;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-family: var(--font-mono);
  font-size: 12px;
  line-height: 1.5;
  resize: vertical;
  outline: none;
  tab-size: 2;
  white-space: pre;
  overflow: auto;
  min-height: 200px;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* ── Detail View ──────────────────────────────────────── */
.detail-view { max-width: 900px; }

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.detail-title { font-size: 24px; font-weight: 700; }
.detail-desc { color: var(--text-secondary); margin-bottom: 16px; font-size: 14px; }

.detail-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.detail-file-tabs {
  display: flex;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius) var(--radius) 0 0;
  overflow-x: auto;
}

.detail-code-block {
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-top: none;
  border-radius: 0 0 var(--radius) var(--radius);
  overflow: auto;
}

.detail-code-block .code-with-lines {
  display: flex;
  min-height: 60px;
}

.detail-code-block .line-numbers {
  padding: 16px 0;
  padding-right: 12px;
  padding-left: 12px;
  min-width: 48px;
  border-right: 1px solid var(--border-color);
}

.detail-code-block pre {
  margin: 0;
  padding: 16px;
  font-family: var(--font-mono);
  font-size: 13px;
  line-height: 1.5;
  flex: 1;
  overflow-x: auto;
  white-space: pre;
  tab-size: 2;
}

.detail-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.detail-code-header {
  display: flex;
  justify-content: flex-end;
  padding: 8px 12px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

/* ── Version History ──────────────────────────────────── */
.version-list { margin-top: 24px; }
.version-item {
  padding: 12px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  margin-bottom: 8px;
  cursor: pointer;
  transition: all var(--transition);
}
.version-item:hover { border-color: var(--accent-blue); }
.version-item .ver-num { font-weight: 600; color: var(--accent-purple); }
.version-item .ver-date { font-size: 12px; color: var(--text-muted); margin-left: 8px; }

/* ── Empty State ──────────────────────────────────────── */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-muted);
}

.empty-state .empty-art {
  font-size: 48px;
  margin-bottom: 16px;
  line-height: 1;
}

.empty-state h3 {
  font-size: 18px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.empty-state p {
  font-size: 14px;
  margin-bottom: 20px;
}

/* ── Syntax Highlighting ──────────────────────────────── */
.syn-keyword { color: var(--accent-pink); font-weight: 500; }
.syn-string { color: var(--accent-yellow); }
.syn-comment { color: #75715e; font-style: italic; }
.syn-number { color: var(--accent-purple); }
.syn-function { color: var(--accent-green); }
.syn-type { color: var(--accent-blue); font-style: italic; }
.syn-operator { color: var(--accent-pink); }
.syn-tag { color: var(--accent-pink); }
.syn-attr { color: var(--accent-green); }
.syn-attr-value { color: var(--accent-yellow); }
.syn-property { color: var(--accent-blue); }
.syn-builtin { color: var(--accent-blue); }

/* ── Tag colors ───────────────────────────────────────── */
.tag-color-0 { background: rgba(166,226,46,0.2); color: #a6e22e; }
.tag-color-1 { background: rgba(102,217,239,0.2); color: #66d9ef; }
.tag-color-2 { background: rgba(249,38,114,0.2); color: #f92672; }
.tag-color-3 { background: rgba(174,129,255,0.2); color: #ae81ff; }
.tag-color-4 { background: rgba(253,151,31,0.2); color: #fd971f; }
.tag-color-5 { background: rgba(230,219,116,0.2); color: #e6db74; }

/* ── Responsive ───────────────────────────────────────── */
@media (max-width: 768px) {
  .sidebar { display: none; }
  .main-content { padding: 16px; }
  .snippet-grid { grid-template-columns: 1fr; }
  .header-bar { flex-wrap: wrap; }
  .search-box { max-width: 100%; }
  .form-row { grid-template-columns: 1fr; }
}

/* ── Scrollbar ────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* ── Toast ────────────────────────────────────────────── */
.toast {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  padding: 12px 20px;
  border-radius: var(--radius);
  color: var(--text-primary);
  font-size: 13px;
  z-index: 2000;
  opacity: 0;
  transform: translateY(10px);
  transition: all 0.3s ease;
  pointer-events: none;
}
.toast.show { opacity: 1; transform: translateY(0); }

/* ── Mobile sidebar toggle ────────────────────────────── */
.sidebar-toggle {
  display: none;
  position: fixed;
  bottom: 20px;
  left: 20px;
  z-index: 1001;
  background: var(--accent-green);
  color: var(--bg-primary);
  border: none;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  font-size: 20px;
  cursor: pointer;
  box-shadow: var(--shadow-card);
}

@media (max-width: 768px) {
  .sidebar-toggle { display: flex; align-items: center; justify-content: center; }
  .sidebar.open { display: block; position: fixed; z-index: 1000; top: 0; left: 0; height: 100vh; }
}
</style>
</head>
<body>

<div class="app-layout">
  <!-- Sidebar -->
  <aside class="sidebar" id="sidebar">
    <div class="sidebar-brand">
      <h1>SnipStash</h1>
      <p>Code Snippet Manager</p>
    </div>
    <nav class="sidebar-nav">
      <button class="nav-item active" data-view="all" onclick="navigateTo('all')">
        <span class="nav-icon">&#9776;</span> All Snippets
        <span class="nav-count" id="total-count">0</span>
      </button>
      <button class="nav-item" data-view="starred" onclick="navigateTo('starred')">
        <span class="nav-icon">&#9733;</span> Starred
        <span class="nav-count" id="starred-count">0</span>
      </button>
      <button class="nav-item" data-view="public" onclick="navigateTo('public')">
        <span class="nav-icon">&#127760;</span> Public
      </button>
      <button class="nav-item" data-view="private" onclick="navigateTo('private')">
        <span class="nav-icon">&#128274;</span> Private
      </button>
    </nav>

    <div class="sidebar-section">
      <div class="sidebar-section-title">
        Collections
        <button onclick="showNewCollectionModal()" title="New collection">+</button>
      </div>
      <ul class="collection-tree" id="collection-list"></ul>
    </div>

    <div class="sidebar-section lang-stats" id="lang-stats-section">
      <div class="sidebar-section-title">Languages</div>
      <div class="lang-bar" id="lang-bar"></div>
      <div class="lang-legend" id="lang-legend"></div>
    </div>
  </aside>

  <!-- Main content -->
  <main class="main-content">
    <!-- List view -->
    <div id="list-view">
      <div class="header-bar">
        <div class="search-box">
          <span class="search-icon">&#128269;</span>
          <input type="text" id="search-input" placeholder="Search snippets..." oninput="handleSearch(this.value)">
        </div>
        <button class="btn btn-primary" onclick="showCreateModal()">+ New Snippet</button>
      </div>
      <div class="snippet-grid" id="snippet-grid"></div>
      <div class="empty-state" id="empty-state" style="display:none">
        <div class="empty-art">{ }</div>
        <h3>No snippets yet</h3>
        <p>Create your first code snippet to get started</p>
        <button class="btn btn-primary" onclick="showCreateModal()">+ New Snippet</button>
      </div>
    </div>

    <!-- Detail view -->
    <div id="detail-view" class="detail-view" style="display:none"></div>
  </main>
</div>

<!-- Create/Edit Modal -->
<div class="modal-overlay" id="snippet-modal">
  <div class="modal">
    <div class="modal-header">
      <h2 id="modal-title">New Snippet</h2>
      <button class="modal-close" onclick="closeModal()">&times;</button>
    </div>
    <div class="modal-body">
      <div class="form-group">
        <label>Title</label>
        <input type="text" id="inp-title" placeholder="My awesome snippet">
      </div>
      <div class="form-group">
        <label>Description</label>
        <input type="text" id="inp-desc" placeholder="What does this code do?">
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>Tags (comma-separated)</label>
          <input type="text" id="inp-tags" placeholder="utils, helper, api">
        </div>
        <div class="form-group">
          <label>Visibility</label>
          <select id="inp-visibility">
            <option value="public">Public</option>
            <option value="private">Private</option>
          </select>
        </div>
      </div>
      <div class="form-group">
        <label>Code</label>
        <div class="code-editor-wrap">
          <div class="file-tabs" id="editor-tabs"></div>
          <div class="editor-container">
            <div class="line-numbers" id="editor-line-nums">1</div>
            <textarea class="code-textarea" id="inp-code" placeholder="Paste or type your code here..." spellcheck="false" oninput="updateLineNumbers()" onscroll="syncScroll(this)" onkeydown="handleTab(event)"></textarea>
          </div>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>Language (auto-detected if empty)</label>
          <select id="inp-language">
            <option value="">Auto-detect</option>
            <option value="javascript">JavaScript</option>
            <option value="python">Python</option>
            <option value="go">Go</option>
            <option value="rust">Rust</option>
            <option value="html">HTML</option>
            <option value="css">CSS</option>
            <option value="typescript">TypeScript</option>
            <option value="shell">Shell</option>
            <option value="json">JSON</option>
            <option value="yaml">YAML</option>
            <option value="sql">SQL</option>
            <option value="text">Plain Text</option>
          </select>
        </div>
        <div class="form-group">
          <label>Filename</label>
          <input type="text" id="inp-filename" placeholder="main.py">
        </div>
      </div>
      <div class="form-group">
        <label>Collection</label>
        <select id="inp-collection">
          <option value="">None</option>
        </select>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary" id="modal-submit" onclick="saveSnippet()">Create</button>
    </div>
  </div>
</div>

<!-- Collection Modal -->
<div class="modal-overlay" id="collection-modal">
  <div class="modal" style="max-width:400px">
    <div class="modal-header">
      <h2 id="coll-modal-title">New Collection</h2>
      <button class="modal-close" onclick="closeCollectionModal()">&times;</button>
    </div>
    <div class="modal-body">
      <div class="form-group">
        <label>Name</label>
        <input type="text" id="inp-coll-name" placeholder="My Collection">
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="closeCollectionModal()">Cancel</button>
      <button class="btn btn-primary" onclick="saveCollection()">Create</button>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>
<button class="sidebar-toggle" onclick="toggleSidebar()">&#9776;</button>

<script>
// ── State ─────────────────────────────────────────────────────
let currentView = 'all';
let currentSnippetId = null;
let editingSnippetId = null;
let editorFiles = [{ filename: 'main.py', code: '', language: '' }];
let activeFileIndex = 0;
let searchDebounce = null;

// ── Tag colors ───────────────────────────────────────────────
const TAG_COLORS = ['tag-color-0','tag-color-1','tag-color-2','tag-color-3','tag-color-4','tag-color-5'];
function tagColor(tag) { let h=0; for(let i=0;i<tag.length;i++) h=((h<<5)-h)+tag.charCodeAt(i); return TAG_COLORS[Math.abs(h)%TAG_COLORS.length]; }

// ── Language colors ──────────────────────────────────────────
const LANG_COLORS = {
  javascript:'#f1e05a', python:'#3572A5', go:'#00ADD8', rust:'#dea584',
  html:'#e34c26', css:'#563d7c', typescript:'#3178c6', ruby:'#701516',
  java:'#b07219', shell:'#89e051', json:'#292929', yaml:'#cb171e',
  sql:'#e38c00', text:'#888888', markdown:'#083fa1'
};

// ── API calls ────────────────────────────────────────────────
async function api(path, opts={}) {
  const res = await fetch('/api'+path, {
    headers: {'Content-Type':'application/json'},
    ...opts,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  return res.json();
}

// ── Toast ────────────────────────────────────────────────────
function toast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2000);
}

// ── Navigation ───────────────────────────────────────────────
function navigateTo(view) {
  currentView = view;
  currentSnippetId = null;
  document.querySelectorAll('.nav-item').forEach(el => el.classList.toggle('active', el.dataset.view === view));
  document.querySelectorAll('.collection-item').forEach(el => el.classList.remove('active'));
  document.getElementById('list-view').style.display = '';
  document.getElementById('detail-view').style.display = 'none';
  document.getElementById('search-input').value = '';
  loadSnippets();
}

function navigateToCollection(cid) {
  currentView = 'collection:' + cid;
  currentSnippetId = null;
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.collection-item').forEach(el => el.classList.toggle('active', el.dataset.cid === cid));
  document.getElementById('list-view').style.display = '';
  document.getElementById('detail-view').style.display = 'none';
  loadSnippets();
}

// ── Load data ────────────────────────────────────────────────
async function loadSnippets() {
  let params = '';
  if (currentView === 'starred') params = '?starred=1';
  else if (currentView === 'public') params = '?visibility=public';
  else if (currentView === 'private') params = '?visibility=private';
  else if (currentView.startsWith('collection:')) params = '?collection_id=' + currentView.split(':')[1];

  const snippets = await api('/snippets' + params);
  renderSnippetGrid(snippets);
  updateCounts();
  loadLangStats();
}

async function updateCounts() {
  const all = await api('/snippets');
  const starred = await api('/snippets?starred=1');
  document.getElementById('total-count').textContent = all.length;
  document.getElementById('starred-count').textContent = starred.length;
}

async function loadCollections() {
  const colls = await api('/collections');
  const list = document.getElementById('collection-list');
  list.innerHTML = colls.map(c => `
    <li class="collection-item" data-cid="${c.id}" onclick="navigateToCollection('${c.id}')">
      <span class="coll-icon">&#128193;</span> ${escHtml(c.name)}
    </li>
  `).join('');

  // Update collection dropdown in modal
  const sel = document.getElementById('inp-collection');
  sel.innerHTML = '<option value="">None</option>' + colls.map(c =>
    `<option value="${c.id}">${escHtml(c.name)}</option>`
  ).join('');
}

async function loadLangStats() {
  const stats = await api('/stats/languages');
  const total = stats.reduce((s,l) => s + l.count, 0);
  if (total === 0) {
    document.getElementById('lang-stats-section').style.display = 'none';
    return;
  }
  document.getElementById('lang-stats-section').style.display = '';

  document.getElementById('lang-bar').innerHTML = stats.map(l =>
    `<div class="lang-bar-segment" style="width:${(l.count/total*100)}%;background:${l.color}" title="${l.language}: ${l.count}"></div>`
  ).join('');

  document.getElementById('lang-legend').innerHTML = stats.slice(0, 6).map(l =>
    `<span class="lang-legend-item"><span class="lang-dot" style="background:${l.color}"></span>${l.language} (${l.count})</span>`
  ).join('');
}

// ── Render snippet cards ─────────────────────────────────────
function renderSnippetGrid(snippets) {
  const grid = document.getElementById('snippet-grid');
  const empty = document.getElementById('empty-state');

  if (snippets.length === 0) {
    grid.innerHTML = '';
    empty.style.display = '';
    return;
  }
  empty.style.display = 'none';

  grid.innerHTML = snippets.map(s => {
    const mainFile = s.files[0] || {};
    const lang = mainFile.language || 'text';
    const color = LANG_COLORS[lang] || '#888';
    const code = mainFile.code || '';
    const preview = highlightCode(code.substring(0, 300), lang);
    const tags = (s.tags||[]).map((t,i) => `<span class="tag-chip ${tagColor(t)}">${escHtml(t)}</span>`).join('');
    const fileCount = s.files.length;
    const timeAgo = formatTimeAgo(s.updated_at);

    return `
      <div class="snippet-card" onclick="showDetail('${s.id}')">
        <div class="card-header">
          <span class="card-title">${escHtml(s.title)}</span>
          <div class="card-badges">
            ${fileCount > 1 ? `<span class="lang-badge" title="${fileCount} files">&#128196; ${fileCount}</span>` : ''}
            <span class="lang-badge"><span class="lang-dot" style="background:${color}"></span>${lang}</span>
            <span class="visibility-badge ${s.visibility}">${s.visibility}</span>
          </div>
        </div>
        ${s.description ? `<div class="card-desc">${escHtml(s.description)}</div>` : ''}
        <div class="card-code"><pre>${preview}</pre></div>
        <div class="card-footer">
          <div class="card-tags">${tags}</div>
          <div class="card-actions">
            <button class="${s.starred ? 'starred' : ''}" onclick="event.stopPropagation();toggleStar('${s.id}')" title="Star">&#9733;</button>
            <button onclick="event.stopPropagation();copyCode('${s.id}')" title="Copy"><span class="copy-icon">&#128203;</span></button>
            <span class="card-meta">${timeAgo}</span>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// ── Detail view ──────────────────────────────────────────────
async function showDetail(sid) {
  const s = await api('/snippets/' + sid);
  if (s.error) { toast('Snippet not found'); return; }
  currentSnippetId = sid;

  document.getElementById('list-view').style.display = 'none';
  const dv = document.getElementById('detail-view');
  dv.style.display = '';

  const tags = (s.tags||[]).map((t,i) => `<span class="tag-chip ${tagColor(t)}">${escHtml(t)}</span>`).join('');
  const mainLang = s.files[0]?.language || 'text';
  const mainColor = LANG_COLORS[mainLang] || '#888';

  let fileTabs = '';
  let codeBlocks = '';
  s.files.forEach((f, i) => {
    const fcolor = LANG_COLORS[f.language] || '#888';
    fileTabs += `<button class="file-tab ${i===0?'active':''}" onclick="switchDetailTab(${i})" data-fidx="${i}">
      <span class="lang-dot" style="background:${fcolor}"></span>${escHtml(f.filename)}
    </button>`;
    const lines = (f.code||'').split('\n');
    const lineNums = lines.map((_,j)=>j+1).join('\n');
    const highlighted = highlightCode(f.code||'', f.language||'text');
    codeBlocks += `<div class="detail-file-block" data-fidx="${i}" style="${i>0?'display:none':''}">
      <div class="detail-code-block">
        <div class="detail-code-header">
          <button class="copy-btn" onclick="copyText(\`${escJs(f.code||'')}\`, this)">
            <span class="copy-icon">&#128203;</span><span class="check">&#10003;</span> Copy
          </button>
        </div>
        <div class="code-with-lines">
          <div class="line-numbers">${lineNums}</div>
          <pre>${highlighted}</pre>
        </div>
      </div>
    </div>`;
  });

  dv.innerHTML = `
    <div class="detail-header">
      <div>
        <div class="detail-title">${escHtml(s.title)}</div>
        ${s.description ? `<div class="detail-desc">${escHtml(s.description)}</div>` : ''}
        <div class="detail-meta">
          <span class="lang-badge"><span class="lang-dot" style="background:${mainColor}"></span>${mainLang}</span>
          <span class="visibility-badge ${s.visibility}">${s.visibility}</span>
          ${tags}
          <span class="card-meta">Updated ${formatTimeAgo(s.updated_at)}</span>
          ${s.fork_of ? '<span class="card-meta">&#127860; Forked</span>' : ''}
          <span class="card-meta">&#128279; ${s.slug}</span>
        </div>
      </div>
      <div class="detail-actions">
        <button class="btn-icon ${s.starred ? 'starred' : ''}" onclick="toggleStar('${s.id}');setTimeout(()=>showDetail('${s.id}'),200)" title="Star">&#9733;</button>
        <button class="btn-icon" onclick="forkSnippet('${s.id}')" title="Fork">&#127860;</button>
        <button class="btn btn-secondary" onclick="showEditModal('${s.id}')">Edit</button>
        <button class="btn btn-danger" onclick="deleteSnippet('${s.id}')">Delete</button>
        <button class="btn btn-secondary" onclick="navigateTo(currentView==='starred'?'starred':'all')">Back</button>
      </div>
    </div>
    <div class="detail-file-tabs">${fileTabs}</div>
    ${codeBlocks}
    ${s.versions && s.versions.length > 0 ? `
      <div class="version-list">
        <h3 style="margin-bottom:12px;color:var(--text-secondary);font-size:14px">Version History (${s.versions.length})</h3>
        ${s.versions.map(v => `
          <div class="version-item">
            <span class="ver-num">v${v.version}</span>
            <span class="ver-date">${formatTimeAgo(v.updated_at)}</span>
            <span style="margin-left:8px;font-size:12px;color:var(--text-muted)">${escHtml(v.title)}</span>
          </div>
        `).join('')}
      </div>
    ` : ''}
  `;
}

function switchDetailTab(idx) {
  document.querySelectorAll('.detail-file-block').forEach(el =>
    el.style.display = parseInt(el.dataset.fidx) === idx ? '' : 'none'
  );
  document.querySelectorAll('.detail-file-tabs .file-tab').forEach(el =>
    el.classList.toggle('active', parseInt(el.dataset.fidx) === idx)
  );
}

// ── CRUD actions ─────────────────────────────────────────────
function showCreateModal() {
  editingSnippetId = null;
  editorFiles = [{ filename: 'main.py', code: '', language: '' }];
  activeFileIndex = 0;
  document.getElementById('modal-title').textContent = 'New Snippet';
  document.getElementById('modal-submit').textContent = 'Create';
  document.getElementById('inp-title').value = '';
  document.getElementById('inp-desc').value = '';
  document.getElementById('inp-tags').value = '';
  document.getElementById('inp-visibility').value = 'public';
  document.getElementById('inp-language').value = '';
  document.getElementById('inp-filename').value = 'main.py';
  document.getElementById('inp-code').value = '';
  document.getElementById('inp-collection').value = '';
  renderEditorTabs();
  updateLineNumbers();
  document.getElementById('snippet-modal').classList.add('active');
}

async function showEditModal(sid) {
  const s = await api('/snippets/' + sid);
  if (s.error) return;
  editingSnippetId = sid;
  editorFiles = s.files.map(f => ({...f}));
  activeFileIndex = 0;
  document.getElementById('modal-title').textContent = 'Edit Snippet';
  document.getElementById('modal-submit').textContent = 'Save';
  document.getElementById('inp-title').value = s.title;
  document.getElementById('inp-desc').value = s.description||'';
  document.getElementById('inp-tags').value = (s.tags||[]).join(', ');
  document.getElementById('inp-visibility').value = s.visibility;
  document.getElementById('inp-language').value = editorFiles[0].language||'';
  document.getElementById('inp-filename').value = editorFiles[0].filename||'';
  document.getElementById('inp-code').value = editorFiles[0].code||'';
  document.getElementById('inp-collection').value = s.collection_id||'';
  renderEditorTabs();
  updateLineNumbers();
  document.getElementById('snippet-modal').classList.add('active');
}

function closeModal() {
  document.getElementById('snippet-modal').classList.remove('active');
}

async function saveSnippet() {
  // Save current editor state to files array
  editorFiles[activeFileIndex].code = document.getElementById('inp-code').value;
  editorFiles[activeFileIndex].language = document.getElementById('inp-language').value;
  editorFiles[activeFileIndex].filename = document.getElementById('inp-filename').value;

  const data = {
    title: document.getElementById('inp-title').value || 'Untitled',
    description: document.getElementById('inp-desc').value,
    tags: document.getElementById('inp-tags').value.split(',').map(t=>t.trim()).filter(Boolean),
    visibility: document.getElementById('inp-visibility').value,
    files: editorFiles,
    collection_id: document.getElementById('inp-collection').value || null,
  };

  if (editingSnippetId) {
    await api('/snippets/' + editingSnippetId, { method: 'PUT', body: data });
    toast('Snippet updated');
  } else {
    await api('/snippets', { method: 'POST', body: data });
    toast('Snippet created');
  }

  closeModal();
  loadSnippets();
  loadCollections();
  if (currentSnippetId) showDetail(currentSnippetId);
}

async function deleteSnippet(sid) {
  if (!confirm('Delete this snippet?')) return;
  await api('/snippets/' + sid, { method: 'DELETE' });
  toast('Snippet deleted');
  navigateTo('all');
}

async function toggleStar(sid) {
  await api('/snippets/' + sid + '/star', { method: 'POST' });
  loadSnippets();
}

async function forkSnippet(sid) {
  const forked = await api('/snippets/' + sid + '/fork', { method: 'POST' });
  toast('Snippet forked');
  showDetail(forked.id);
}

async function copyCode(sid) {
  const s = await api('/snippets/' + sid);
  const code = s.files.map(f => f.code).join('\n\n');
  await navigator.clipboard.writeText(code);
  toast('Copied to clipboard');
}

function copyText(text, btn) {
  navigator.clipboard.writeText(text);
  btn.classList.add('copied');
  setTimeout(() => btn.classList.remove('copied'), 1500);
}

// ── Editor file tabs ─────────────────────────────────────────
function renderEditorTabs() {
  const container = document.getElementById('editor-tabs');
  container.innerHTML = editorFiles.map((f, i) =>
    `<button class="file-tab ${i===activeFileIndex?'active':''}" onclick="switchEditorTab(${i})">
      ${escHtml(f.filename||'untitled')}
      ${editorFiles.length > 1 ? `<span class="tab-close" onclick="event.stopPropagation();removeEditorFile(${i})">&times;</span>` : ''}
    </button>`
  ).join('') + '<button class="add-file-tab" onclick="addEditorFile()">+</button>';
}

function switchEditorTab(idx) {
  // Save current
  editorFiles[activeFileIndex].code = document.getElementById('inp-code').value;
  editorFiles[activeFileIndex].language = document.getElementById('inp-language').value;
  editorFiles[activeFileIndex].filename = document.getElementById('inp-filename').value;
  // Switch
  activeFileIndex = idx;
  document.getElementById('inp-code').value = editorFiles[idx].code || '';
  document.getElementById('inp-language').value = editorFiles[idx].language || '';
  document.getElementById('inp-filename').value = editorFiles[idx].filename || '';
  renderEditorTabs();
  updateLineNumbers();
}

function addEditorFile() {
  editorFiles[activeFileIndex].code = document.getElementById('inp-code').value;
  editorFiles[activeFileIndex].language = document.getElementById('inp-language').value;
  editorFiles[activeFileIndex].filename = document.getElementById('inp-filename').value;
  editorFiles.push({ filename: 'file' + (editorFiles.length+1) + '.txt', code: '', language: '' });
  activeFileIndex = editorFiles.length - 1;
  document.getElementById('inp-code').value = '';
  document.getElementById('inp-language').value = '';
  document.getElementById('inp-filename').value = editorFiles[activeFileIndex].filename;
  renderEditorTabs();
  updateLineNumbers();
}

function removeEditorFile(idx) {
  if (editorFiles.length <= 1) return;
  editorFiles.splice(idx, 1);
  if (activeFileIndex >= editorFiles.length) activeFileIndex = editorFiles.length - 1;
  document.getElementById('inp-code').value = editorFiles[activeFileIndex].code || '';
  document.getElementById('inp-language').value = editorFiles[activeFileIndex].language || '';
  document.getElementById('inp-filename').value = editorFiles[activeFileIndex].filename || '';
  renderEditorTabs();
  updateLineNumbers();
}

// ── Line numbers & tab support ───────────────────────────────
function updateLineNumbers() {
  const code = document.getElementById('inp-code').value;
  const lines = code.split('\n').length;
  document.getElementById('editor-line-nums').textContent = Array.from({length:lines},(_,i)=>i+1).join('\n');
}

function syncScroll(textarea) {
  document.getElementById('editor-line-nums').scrollTop = textarea.scrollTop;
}

function handleTab(e) {
  if (e.key === 'Tab') {
    e.preventDefault();
    const ta = e.target;
    const start = ta.selectionStart;
    const end = ta.selectionEnd;
    ta.value = ta.value.substring(0, start) + '  ' + ta.value.substring(end);
    ta.selectionStart = ta.selectionEnd = start + 2;
    updateLineNumbers();
  }
}

// ── Search ───────────────────────────────────────────────────
function handleSearch(query) {
  clearTimeout(searchDebounce);
  searchDebounce = setTimeout(async () => {
    if (!query.trim()) { loadSnippets(); return; }
    const results = await api('/snippets/search?q=' + encodeURIComponent(query));
    renderSnippetGrid(results);
  }, 200);
}

// ── Collections modal ────────────────────────────────────────
function showNewCollectionModal() {
  document.getElementById('inp-coll-name').value = '';
  document.getElementById('collection-modal').classList.add('active');
}

function closeCollectionModal() {
  document.getElementById('collection-modal').classList.remove('active');
}

async function saveCollection() {
  const name = document.getElementById('inp-coll-name').value || 'Untitled';
  await api('/collections', { method: 'POST', body: { name } });
  toast('Collection created');
  closeCollectionModal();
  loadCollections();
}

// ── Sidebar toggle (mobile) ─────────────────────────────────
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

// ── Syntax Highlighting ──────────────────────────────────────
function highlightCode(code, language) {
  if (!code) return '';
  code = escHtml(code);

  const rules = {
    javascript: [
      [/\b(const|let|var|function|return|if|else|for|while|do|switch|case|break|continue|new|this|class|extends|import|export|from|default|async|await|try|catch|finally|throw|typeof|instanceof|in|of|yield|void|delete|null|undefined|true|false)\b/g, 'syn-keyword'],
      [/(\/\/[^\n]*)/g, 'syn-comment'],
      [/(\/\*[\s\S]*?\*\/)/g, 'syn-comment'],
      [/(&quot;(?:[^&]|&(?!quot;))*?&quot;|&#x27;(?:[^&]|&(?!#x27;))*?&#x27;|`(?:[^`\\]|\\.)*`)/g, 'syn-string'],
      [/\b(\d+\.?\d*)\b/g, 'syn-number'],
      [/\b(console|document|window|Math|Array|Object|String|Number|Boolean|Promise|JSON|Map|Set|Error|RegExp|Date)\b/g, 'syn-builtin'],
      [/(\w+)\s*(?=\()/g, 'syn-function'],
    ],
    python: [
      [/\b(def|class|return|if|elif|else|for|while|import|from|as|try|except|finally|raise|with|yield|lambda|pass|break|continue|and|or|not|is|in|True|False|None|self|global|nonlocal|assert|del|async|await)\b/g, 'syn-keyword'],
      [/(#[^\n]*)/g, 'syn-comment'],
      [/(&quot;&quot;&quot;[\s\S]*?&quot;&quot;&quot;|&#x27;&#x27;&#x27;[\s\S]*?&#x27;&#x27;&#x27;)/g, 'syn-string'],
      [/(f?&quot;(?:[^&\\]|&(?!quot;)|\\.)* ?&quot;|f?&#x27;(?:[^&\\]|&(?!#x27;)|\\.)* ?&#x27;)/g, 'syn-string'],
      [/\b(\d+\.?\d*)\b/g, 'syn-number'],
      [/\b(print|len|range|int|str|float|list|dict|set|tuple|type|isinstance|super|input|open|map|filter|zip|enumerate|sorted|reversed|any|all|min|max|sum|abs|round)\b/g, 'syn-builtin'],
      [/@(\w+)/g, 'syn-function'],
      [/(\w+)\s*(?=\()/g, 'syn-function'],
    ],
    go: [
      [/\b(func|package|import|return|if|else|for|range|switch|case|default|break|continue|go|defer|chan|select|type|struct|interface|map|var|const|nil|true|false|make|new|append|len|cap|delete|copy|close|panic|recover)\b/g, 'syn-keyword'],
      [/(\/\/[^\n]*)/g, 'syn-comment'],
      [/(\/\*[\s\S]*?\*\/)/g, 'syn-comment'],
      [/(&quot;(?:[^&\\]|&(?!quot;)|\\.)* ?&quot;|`[^`]*`)/g, 'syn-string'],
      [/\b(\d+\.?\d*)\b/g, 'syn-number'],
      [/\b(string|int|int8|int16|int32|int64|float32|float64|bool|byte|rune|error|uint|uint8|uint16|uint32|uint64)\b/g, 'syn-type'],
      [/\b(fmt|log|os|io|net|http|json|strings|strconv|time|context|sync|errors)\b/g, 'syn-builtin'],
      [/(\w+)\s*(?=\()/g, 'syn-function'],
    ],
    rust: [
      [/\b(fn|let|mut|const|pub|use|mod|struct|enum|impl|trait|type|where|for|while|loop|if|else|match|return|break|continue|move|ref|self|Self|super|crate|as|in|unsafe|async|await|dyn|true|false|None|Some|Ok|Err)\b/g, 'syn-keyword'],
      [/(\/\/[^\n]*)/g, 'syn-comment'],
      [/(\/\*[\s\S]*?\*\/)/g, 'syn-comment'],
      [/(&quot;(?:[^&\\]|&(?!quot;)|\\.)* ?&quot;)/g, 'syn-string'],
      [/\b(\d+\.?\d*)\b/g, 'syn-number'],
      [/\b(i8|i16|i32|i64|i128|u8|u16|u32|u64|u128|f32|f64|bool|char|str|String|Vec|Box|Rc|Arc|Option|Result|HashMap|HashSet|usize|isize)\b/g, 'syn-type'],
      [/(\w+)\s*(?=\()/g, 'syn-function'],
      [/(\w+)!/g, 'syn-function'],
    ],
    html: [
      [/(&lt;\/?)([\w-]+)/g, function(m, bracket, tag) { return `<span class="syn-operator">${bracket}</span><span class="syn-tag">${tag}</span>`; }],
      [/(\w+)(=)/g, function(m, attr, eq) { return `<span class="syn-attr">${attr}</span><span class="syn-operator">${eq}</span>`; }],
      [/(&quot;[^&]*?&quot;)/g, 'syn-attr-value'],
      [/(&lt;!--[\s\S]*?--&gt;)/g, 'syn-comment'],
    ],
    css: [
      [/([.#]?[\w-]+)\s*(?=\{)/g, 'syn-tag'],
      [/([\w-]+)\s*(?=:)/g, 'syn-property'],
      [/(\/\*[\s\S]*?\*\/)/g, 'syn-comment'],
      [/(&quot;[^&]*?&quot;|&#x27;[^&]*?&#x27;)/g, 'syn-string'],
      [/\b(\d+\.?\d*(px|em|rem|%|vh|vw|s|ms|deg)?)\b/g, 'syn-number'],
      [/\b(inherit|initial|none|auto|flex|grid|block|inline|relative|absolute|fixed|sticky)\b/g, 'syn-keyword'],
      [/(#[0-9a-fA-F]{3,8})\b/g, 'syn-number'],
    ],
  };

  const langRules = rules[language] || rules['javascript'] || [];

  // Apply rules in order. Simple approach: apply each rule sequentially
  // but skip already-highlighted content
  for (const rule of langRules) {
    const [pattern, replacement] = rule;
    if (typeof replacement === 'function') {
      code = code.replace(pattern, replacement);
    } else {
      code = code.replace(pattern, (match) => {
        if (match.includes('class="syn-')) return match; // skip already highlighted
        return `<span class="${replacement}">${match}</span>`;
      });
    }
  }

  return code;
}

// ── Helpers ──────────────────────────────────────────────────
function escHtml(s) {
  if (!s) return '';
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
          .replace(/"/g,'&quot;').replace(/'/g,'&#x27;');
}

function escJs(s) {
  if (!s) return '';
  return s.replace(/\\/g,'\\\\').replace(/`/g,'\\`').replace(/\$/g,'\\$');
}

function formatTimeAgo(iso) {
  if (!iso) return '';
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return mins + 'm ago';
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return hrs + 'h ago';
  const days = Math.floor(hrs / 24);
  return days + 'd ago';
}

// ── Check URL for shared slug ────────────────────────────────
async function checkSlugRoute() {
  const path = window.location.pathname;
  if (path.startsWith('/s/')) {
    const slug = path.substring(3);
    const s = await api('/snippets/slug/' + slug);
    if (!s.error) {
      showDetail(s.id);
      return;
    }
  }
  loadSnippets();
}

// ── Init ─────────────────────────────────────────────────────
loadCollections();
checkSlugRoute();
</script>
</body>
</html>"""
