# ax-test-snippets

## What This Is

A beautiful code snippet manager — GitHub Gist meets Raycast. A web app where developers can create, organize, search, and share code snippets with stunning Monokai-inspired dark UI, syntax highlighting, multi-file support, and versioning. Built with Python/Flask backend and a polished vanilla HTML/CSS/JS frontend.

## Core Value

Developers can instantly save, organize, and share code snippets with syntax-highlighted, visually striking presentation — fast to use, beautiful to look at.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] CRUD operations for snippets (title, description, code, language, tags, visibility, timestamps)
- [ ] Multi-file snippets (each with filename, code, language)
- [ ] Auto-detect language from code content or file extension
- [ ] Collections/folders to organize snippets
- [ ] Full-text search across title, description, code content
- [ ] Snippet forking (copy public snippets to your collection)
- [ ] Snippet versioning with edit history and diffs
- [ ] Shareable links with unique slugs
- [ ] Language statistics (count per language)
- [ ] Star/favorite snippets
- [ ] In-memory storage (no database required)
- [ ] Monokai-inspired dark theme with colorful syntax
- [ ] Custom CSS-based syntax highlighter (JS, Python, Go, Rust, HTML, CSS)
- [ ] Card-based layout with hover lift effects and shadows
- [ ] Code editor textarea with monospace font, line numbers, tab support
- [ ] File tabs for multi-file snippets (VS Code style)
- [ ] Tag chips with colored backgrounds
- [ ] Collection sidebar with tree-style navigation
- [ ] Search with instant results and highlighted matches
- [ ] Copy-to-clipboard with animated checkmark feedback
- [ ] Responsive masonry grid for snippet cards
- [ ] Elegant empty states with CSS art or unicode illustrations
- [ ] Language icon badges (colored dots per language)

### Out of Scope

- User authentication/accounts — single-user, no login required
- Database persistence — in-memory storage only
- Real-time collaboration — not needed for v1
- Mobile native app — web-only
- Server-side rendering — static frontend with API calls

## Context

- Stack: Python 3.12 + Flask for backend API
- Frontend: Vanilla HTML, CSS, JavaScript (no framework)
- Deployment: Vercel (serverless Python)
- Entry point: api/index.py importing from app module
- Storage: In-memory Python data structures (lists/dicts)
- No external dependencies beyond Flask
- Syntax highlighting done entirely in CSS/JS (no external library)

## Constraints

- **Stack**: Python/Flask — specified requirement
- **Deployment**: Vercel serverless — api/index.py entry point with @vercel/python
- **Storage**: In-memory only — no database, no file system persistence
- **Frontend**: No JS frameworks — vanilla HTML/CSS/JS with custom syntax highlighter
- **Theme**: Monokai-inspired dark theme — non-negotiable design requirement

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| In-memory storage | Simplicity, no database setup needed, fast for demo | -- Pending |
| Custom CSS syntax highlighter | No external dependencies, full control over styling | -- Pending |
| Vanilla JS frontend | No build step, simple deployment, fast load times | -- Pending |
| Flask backend | Lightweight, Vercel-compatible, Pythonic | -- Pending |

---
*Last updated: 2026-03-10 after initialization*
