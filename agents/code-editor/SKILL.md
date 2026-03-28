---
name: code-edit
description: >
  Apply a natural language edit instruction to a file in a repository.
  Handles frontend, backend, config, and template files.
---

## Steps

1. Parse instruction → identify: what changes, which layer (UI/API/config)
2. Use memory context (runtime, framework, repo path) to locate file
3. Read file via file_read tool
4. Generate minimal edit
5. Output unified diff
6. On user confirmation → write via file_write tool

## Patterns

### Styling
- CSS files: find property, replace value
- Tailwind: find className, update utility class
- Inline styles in JSX/HTML: find style attribute, update

### Layout / Components
- Logo: find <header> or Navbar, insert <img> or component import
- Nav links: find <nav> or <ul>, insert <li><a>

### Backend
- Flask route: find last @app.route, insert new route after
- Express route: find router.get/post block, insert new one
- Go handler: find http.HandleFunc block, insert new one

### Config
- package.json scripts: find "scripts" key, add/update entry
- requirements.txt: append new package

## Guardrails
- Never touch .env files
- Never delete functions/classes unless explicitly told
- If target is ambiguous, list candidates and ask