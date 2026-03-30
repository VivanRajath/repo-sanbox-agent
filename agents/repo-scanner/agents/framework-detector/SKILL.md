---
name: framework-detect
description: >
  Detect runtime, framework, version, entry point, and commands
  from repository manifest files. Returns partial JSON for the
  parent scanner to assemble.
---

## Scope
- Reading and parsing manifest files (package.json, requirements.txt,
  go.mod, Cargo.toml, Gemfile, pom.xml, build.gradle, Dockerfile)
- Extracting: runtime, version_hint, entry, install_cmd, run_cmd,
  port, framework

## Steps
1. Receive repo root path from parent scanner.
2. Read the root directory listing via file-read.
3. Match files against detection order (see SOUL.md).
4. Read the matched manifest file via file-read.
5. Extract runtime, version_hint, framework, entry, install_cmd,
   run_cmd, and port.
6. Return partial JSON with these fields only.

## Output Example
```json
{
  "runtime": "python",
  "version_hint": "3.11",
  "entry": "app.py",
  "install_cmd": "pip install -r requirements.txt",
  "run_cmd": "python app.py",
  "port": 5000,
  "framework": "flask"
}
```

## Guardrails
- Read-only. Never write or modify any file.
- Never execute shell commands.
- If runtime is ambiguous, return "unknown" and list root files.
