# repo-sandbox-agent

## Agent 1: repo-scanner

**Input:** repo path (local)
**Output:** structured JSON
```json
{
  "runtime": "python | node | go | rust | ruby | java | docker | unknown",
  "version_hint": "3.11 | 18 | 1.21 | ...",
  "entry": "app.py | index.js | main.go | ...",
  "install_cmd": "pip install -r requirements.txt",
  "run_cmd": "python app.py",
  "port": 8000,
  "framework": "flask | fastapi | express | nextjs | gin | unknown",
  "env_vars_needed": ["DATABASE_URL", "SECRET_KEY"],
  "file_structure": "Directory tree (max depth 3)",
  "context_summary": "High-level summary of architecture and dependencies"
}
```

The host environment consumes this JSON to:
- Choose the correct sandbox runtime
- Run install_cmd then run_cmd
- Expose the correct port for preview
- Feed `file_structure` and `context_summary` to subsequent editor agents

## Agent 2: intent-router

**Input:** natural language instruction + repo-scanner JSON
**Output:** assigned tier: `jnr`, `mid`, or `snr`

Evaluates the complexity of the user query against the codebase structure and assigns it to the appropriate tier to save LLM cost.

## Agent 3: code-editor (Tiered)

**Input:** natural language instruction + repo path + runtime context (from scanner) + intent tier
**Output:** unified diff → patched file on confirmation

Based on the `intent-router`'s decision, one of three models is invoked:
- **Jnr Coder (`jnr`)**: Handles small logic fixes, single file edits, or minor styling changes. (Low LLM cost)
- **Mid Coder (`mid`)**: Handles multi-file feature additions, basic refactors, and component creation. (Standard LLM cost)
- **Snr Coder (`snr`)**: Handles system architecture changes, severe debugging, and deep exploratory file searching. (High LLM cost. Has leeway to use shell commands to query deeper file structure beyond the scanner's depth 3 limit).

Examples:
- "change the background color to red" -> `jnr`
- "add a logo to the navbar" -> `jnr`
- "add a /health endpoint router and module" -> `mid`
- "refactor the database layer to use a connection pool and resolve the memory leak" -> `snr`

## Delegation
Orchestrator routes based on user message:
- Contains a repo path → repo-scanner
- Contains an edit instruction → intent-router -> code-editor (Jnr/Mid/Snr)
- Both → scanner first, then intent-router, then editor