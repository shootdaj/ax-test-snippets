# Requirements — ax-test-snippets

## v1 Requirements

### Snippets (SNIP)
- [ ] **SNIP-01**: User can create a snippet with title, description, code, language, tags, and visibility (public/private)
- [ ] **SNIP-02**: User can view a snippet with syntax-highlighted code display
- [ ] **SNIP-03**: User can edit an existing snippet's title, description, code, language, tags, and visibility
- [ ] **SNIP-04**: User can delete a snippet
- [ ] **SNIP-05**: User can create multi-file snippets (each file has filename, code, language)
- [ ] **SNIP-06**: User can view multi-file snippets with VS Code-style file tabs
- [ ] **SNIP-07**: User can star/favorite a snippet and view starred snippets
- [ ] **SNIP-08**: User can fork a public snippet to their own collection
- [ ] **SNIP-09**: User can view snippet version history with diffs between versions
- [ ] **SNIP-10**: User can share a snippet via a unique slug URL

### Search & Discovery (SRCH)
- [ ] **SRCH-01**: User can search across snippet titles, descriptions, and code content with instant results
- [ ] **SRCH-02**: Search results highlight matching terms in context
- [ ] **SRCH-03**: User can view language statistics (count of snippets per language)
- [ ] **SRCH-04**: User can filter snippets by language, tags, or visibility

### Collections (COLL)
- [ ] **COLL-01**: User can create, rename, and delete collections (folders)
- [ ] **COLL-02**: User can add/remove snippets to/from collections
- [ ] **COLL-03**: User can browse collections in a tree-style sidebar navigation

### Syntax & Editor (EDIT)
- [ ] **EDIT-01**: Code is displayed with CSS-based syntax highlighting (keywords, strings, comments) for JS, Python, Go, Rust, HTML, CSS
- [ ] **EDIT-02**: Code editor textarea has monospace font, line numbers, and tab key support
- [ ] **EDIT-03**: Language is auto-detected from code content or file extension when not specified

### UI & Design (UI)
- [ ] **UI-01**: App uses a Monokai-inspired dark theme (dark backgrounds, colorful syntax)
- [ ] **UI-02**: Snippets display as cards with hover lift effects and subtle shadows
- [ ] **UI-03**: Responsive masonry grid layout for snippet cards
- [ ] **UI-04**: Tag chips display with colored backgrounds
- [ ] **UI-05**: Language icon badges show as colored dots per language
- [ ] **UI-06**: Copy-to-clipboard button with animated checkmark feedback
- [ ] **UI-07**: Elegant empty states with unicode illustrations
- [ ] **UI-08**: Responsive design that works on desktop and tablet

### Infrastructure (INFRA)
- [ ] **INFRA-01**: Flask API serves both JSON endpoints and HTML frontend
- [ ] **INFRA-02**: All data stored in-memory (Python data structures)
- [ ] **INFRA-03**: App deploys to Vercel via api/index.py entry point

## v2 Requirements (Deferred)
- User authentication and accounts
- Database persistence (PostgreSQL/SQLite)
- Real-time collaboration
- API rate limiting
- Export snippets (download as files)
- Embed snippets in other sites

## Out of Scope
- Mobile native app — web-only for v1
- Real-time collaboration — not needed for single-user
- Server-side rendering — static frontend with API calls
- External syntax highlighting libraries — custom CSS/JS only
- User accounts/login — single-user, no auth required

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SNIP-01 | Phase 1 | Pending |
| SNIP-02 | Phase 1 | Pending |
| SNIP-03 | Phase 1 | Pending |
| SNIP-04 | Phase 1 | Pending |
| SNIP-05 | Phase 2 | Pending |
| SNIP-06 | Phase 2 | Pending |
| SNIP-07 | Phase 3 | Pending |
| SNIP-08 | Phase 3 | Pending |
| SNIP-09 | Phase 3 | Pending |
| SNIP-10 | Phase 3 | Pending |
| SRCH-01 | Phase 4 | Pending |
| SRCH-02 | Phase 4 | Pending |
| SRCH-03 | Phase 4 | Pending |
| SRCH-04 | Phase 4 | Pending |
| COLL-01 | Phase 2 | Pending |
| COLL-02 | Phase 2 | Pending |
| COLL-03 | Phase 2 | Pending |
| EDIT-01 | Phase 1 | Pending |
| EDIT-02 | Phase 1 | Pending |
| EDIT-03 | Phase 1 | Pending |
| UI-01 | Phase 1 | Pending |
| UI-02 | Phase 1 | Pending |
| UI-03 | Phase 1 | Pending |
| UI-04 | Phase 1 | Pending |
| UI-05 | Phase 1 | Pending |
| UI-06 | Phase 1 | Pending |
| UI-07 | Phase 1 | Pending |
| UI-08 | Phase 1 | Pending |
| INFRA-01 | Phase 1 | Pending |
| INFRA-02 | Phase 1 | Pending |
| INFRA-03 | Phase 5 | Pending |

---
*Last updated: 2026-03-10 after requirements definition*
