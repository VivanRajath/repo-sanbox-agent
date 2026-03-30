# repo-sandbox-agent

## Agent Hierarchy

```
repo-sandbox-agent (Orchestrator)
│
├── repo-scanner ─────────────── Scan orchestrator
│   ├── framework-detector ───── Phase 1: manifest reading, runtime detection
│   └── deep-scan-agent ──────── Phase 2: deep traversal, architecture summary
│
├── intent-router ────────────── Classifies edit complexity → assigns tier
│
└── code-editor ──────────────── Edit orchestrator
    ├── jnr-developer ────────── Tier jnr: single-file edits (flash models)
    ├── snr-developer ────────── Tier snr: multi-file features (sonnet models)
    └── architect ────────────── Tier architect: system changes (top-tier models)
```

---

## Agent 1: repo-scanner

**Role:** Scan orchestrator
**Input:** repo path (local)
**Output:** structured JSON

Delegates scanning to two sub-agents in sequence:

### Sub-Agent: framework-detector (Phase 1)

**Input:** repo root path
**Output:** partial JSON (runtime, version_hint, entry, install_cmd, run_cmd, port, framework)

Reads manifest files (package.json, requirements.txt, go.mod, Cargo.toml,
Gemfile, pom.xml, Dockerfile) and pattern-matches to detect runtime and framework.
Uses cheap flash models. Read-only, no shell access.

### Sub-Agent: deep-scan-agent (Phase 2)

**Input:** repo root path
**Output:** partial JSON (file_structure, context_summary, env_vars_needed)

Traverses the full directory tree via shell commands (tree, find, grep).
Discovers env var usage patterns, maps dependencies, and summarizes the
architecture. Uses standard models with shell-exec access.

### Assembled Output
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
  "file_structure": "Directory tree (full depth)",
  "context_summary": "High-level summary of architecture and dependencies"
}
```

The host environment consumes this JSON to:
- Choose the correct sandbox runtime
- Run install_cmd then run_cmd
- Expose the correct port for preview
- Feed file_structure and context_summary to code-editor sub-agents

---

## Agent 2: intent-router

**Input:** natural language instruction + repo-scanner JSON
**Output:** assigned tier: `jnr`, `snr`, or `architect`

Evaluates the complexity of the user query against the codebase structure:
- **Low** (single-file, typo, style) -> `jnr` -> jnr-developer
- **Medium** (multi-file, features, refactors) -> `snr` -> snr-developer
- **High** (architecture, complex debug, system redesign) -> `architect` -> architect

---

## Agent 3: code-editor

**Role:** Edit orchestrator
**Input:** natural language instruction + repo path + runtime context + tier
**Output:** unified diff -> patched file on confirmation

Delegates to exactly one sub-agent per task based on the intent-router's
tier assignment:

### Sub-Agent: jnr-developer (Tier: jnr)

**Model:** google:gemini-2.0-flash (low cost)
**Tools:** file-read, file-write
**Scope:** Single-file edits only

Examples:
- "change the background color to red"
- "add a logo to the navbar"
- "fix the typo in the footer text"

### Sub-Agent: snr-developer (Tier: snr)

**Model:** anthropic:claude-sonnet-4-5-20250514 (standard cost)
**Tools:** file-read, file-write
**Scope:** Multi-file edits within scanner's depth-3 file structure

Examples:
- "add a /health endpoint router and module"
- "create a user profile component with API integration"
- "refactor the auth middleware to support JWT"

### Sub-Agent: architect (Tier: architect)

**Model:** anthropic:claude-sonnet-4-5-20250514 (high cost)
**Tools:** file-read, file-write, shell-exec
**Scope:** Full codebase with shell access for deep exploration

Examples:
- "refactor the database layer to use a connection pool and resolve the memory leak"
- "redesign the event pipeline to support async processing"
- "diagnose and fix the intermittent 502 errors in the API gateway"

---

## Delegation Flow

```
User Message
    │
    ├── contains repo path ──────────> repo-scanner
    │                                    ├── framework-detector (Phase 1)
    │                                    └── deep-scan-agent (Phase 2)
    │
    ├── contains edit instruction ───> intent-router
    │                                    │
    │                                    └── code-editor
    │                                         ├── jnr-developer (if jnr)
    │                                         ├── snr-developer (if snr)
    │                                         └── architect (if architect)
    │
    └── both ────────────────────────> scanner first, then router, then editor
```