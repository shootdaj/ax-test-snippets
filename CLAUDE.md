# ax-test-snippets

## Project
Code snippet manager — Python/Flask backend with vanilla HTML/CSS/JS frontend.
Deployed to Vercel via `api/index.py`.

## Design
- Monokai-inspired dark theme (dark backgrounds: #272822, colorful syntax)
- Custom CSS-based syntax highlighter (no external libs)
- Card-based layout with hover lift effects
- Responsive masonry grid

## Commands
```bash
# Run locally
python -m flask --app api.index run --port 5000

# Run tests
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v -m integration
python -m pytest tests/scenarios/ -v -m scenario
```

# Testing Requirements (AX)

Every feature implementation MUST include tests at all three tiers:

## Test Tiers
1. **Unit tests** — Test individual functions/methods in isolation. Mock external dependencies.
2. **Integration tests** — Test component interactions with real services via docker-compose.test.yml.
3. **Scenario tests** — Test full user workflows end-to-end.

## Test Naming
Use semantic names: `Test<Component>_<Behavior>[_<Condition>]`
- Good: `TestAuthService_LoginWithValidCredentials`, `TestFullCheckoutFlow`
- Bad: `TestShouldWork`, `Test1`, `TestGivenUserWhenLoginThenSuccess`

## Reference
- See `TEST_GUIDE.md` for requirement-to-test mapping
- See `.claude/ax/references/testing-pyramid.md` for full methodology
- Every requirement in ROADMAP.md must map to at least one scenario test
