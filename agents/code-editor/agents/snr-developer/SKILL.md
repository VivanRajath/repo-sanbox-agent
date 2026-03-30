---
name: snr-edit
description: >
  Apply multi-file edits: feature additions, component creation,
  refactors, route setup, and integration tasks.
---

## Scope
- New component/module creation with proper imports and exports
- Route/endpoint setup across router and handler files
- API integration (fetch calls, service modules, type definitions)
- Targeted refactors (extract function, rename across files, restructure)
- Multi-file config changes (package.json + tsconfig, requirements.txt + imports)

## Steps
1. Receive instruction + file paths + runtime context from parent.
2. Read all affected files via file-read tool.
3. Map the dependency relationships between files.
4. Plan the ordered change set (which files, what changes, in what sequence).
5. Generate unified diffs for each affected file.
6. Present all diffs for user confirmation.
7. Write all patched files via file-write tool on confirmation.

## Guardrails
- Stay within the scanner's depth-3 file structure. Do not explore beyond it.
- Do not use shell-exec. File navigation is file-read only.
- Never touch .env or credential files.
- If the change requires deep architecture work or filesystem exploration,
  report back to parent for escalation to architect.
- If target is ambiguous, list candidates and ask.
