# Roadmap — ax-test-snippets

## Overview
**5 phases** | **28 requirements** | All v1 requirements covered

---

## Phase 1: Core CRUD + UI Foundation
**Goal:** Build the Flask API with basic snippet CRUD, in-memory storage, CSS-based syntax highlighting, and the Monokai dark theme with card-based layout.

**Requirements:** SNIP-01, SNIP-02, SNIP-03, SNIP-04, EDIT-01, EDIT-02, EDIT-03, UI-01, UI-02, UI-03, UI-04, UI-05, UI-06, UI-07, UI-08, INFRA-01, INFRA-02

**Success Criteria:**
1. User can create a snippet via form and see it displayed with syntax highlighting
2. User can edit and delete snippets from the UI
3. Code renders with Monokai-themed syntax colors for at least JS and Python
4. Snippet cards display in a responsive masonry grid with hover effects
5. Copy-to-clipboard works with animated checkmark feedback

**Plans:** 3-4

---

## Phase 2: Multi-file Snippets + Collections
**Goal:** Add multi-file snippet support with VS Code-style tabs, and collection/folder organization with sidebar navigation.

**Requirements:** SNIP-05, SNIP-06, COLL-01, COLL-02, COLL-03

**Success Criteria:**
1. User can create a snippet with multiple files, each with its own filename and language
2. Multi-file snippets display with clickable file tabs that switch content
3. User can create collections and add snippets to them
4. Sidebar shows collection tree and clicking a collection filters snippets

**Plans:** 2-3

---

## Phase 3: Social Features — Stars, Forks, Versioning, Sharing
**Goal:** Add starring, forking, version history with diffs, and shareable slug URLs.

**Requirements:** SNIP-07, SNIP-08, SNIP-09, SNIP-10

**Success Criteria:**
1. User can star/unstar snippets and filter to show only starred
2. User can fork a public snippet creating an independent copy
3. Editing a snippet creates a version; user can view version history with diffs
4. Each snippet has a unique shareable slug URL that displays the snippet

**Plans:** 2-3

---

## Phase 4: Search + Discovery
**Goal:** Full-text search across snippets with instant results, match highlighting, language stats, and filtering.

**Requirements:** SRCH-01, SRCH-02, SRCH-03, SRCH-04

**Success Criteria:**
1. User can type in search and see matching snippets instantly (debounced)
2. Search matches are highlighted in results
3. Language statistics page/panel shows snippet counts per language
4. User can filter snippets by language, tag, or visibility

**Plans:** 2

---

## Phase 5: Deployment + Polish
**Goal:** Deploy to Vercel, verify all endpoints work in production, final UI polish.

**Requirements:** INFRA-03

**Success Criteria:**
1. App deploys to Vercel and all API endpoints return correct responses
2. Frontend loads and displays snippets correctly in production
3. All features work end-to-end in deployed environment

**Plans:** 1-2

---

*Last updated: 2026-03-10 after roadmap creation*
