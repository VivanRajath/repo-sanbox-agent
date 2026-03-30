---
name: deep-scan
description: >
  Deep directory traversal, dependency analysis, env var discovery,
  and architecture summarization. Returns partial JSON for the
  parent scanner to assemble.
---

## Scope
- Full directory tree traversal (beyond depth 3)
- Environment variable discovery across all source files
- Dependency graph mapping from imports and configs
- Architecture summarization (layers, modules, data flow)

## Steps
1. Receive repo path from parent scanner.
2. Run `tree -L 6` or `find . -type f` via shell-exec for full structure.
3. Run `grep -r "os.environ\|process.env\|env.Get\|getenv" --include="*.py" --include="*.js" --include="*.ts" --include="*.go"` to discover env vars.
4. Check for .env.example via file-read.
5. Read key architectural files (main entry, router, config) via file-read.
6. Produce:
   - `file_structure`: Full directory tree output
   - `context_summary`: High-level architectural overview
   - `env_vars_needed`: List of discovered environment variables
7. Return partial JSON with these fields only.

## Output Example
```json
{
  "file_structure": "src/\n  api/\n    routes/\n    middleware/\n  models/\n  utils/",
  "context_summary": "Express.js API with layered architecture: routes -> controllers -> models. Uses PostgreSQL via Sequelize ORM.",
  "env_vars_needed": ["DATABASE_URL", "JWT_SECRET", "PORT"]
}
```

## Guardrails
- Read-only. Never write or modify any file.
- Shell commands must be read-only exploration only.
- If the repo is very large, limit tree depth to prevent context overflow.
