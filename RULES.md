# Hard Rules

## Always
- Show a diff summary before applying any file edit.
- Output scanner results as valid JSON.
- Store last scan result in memory/MEMORY.md for code-editor context.

## Never
- Clone, run, or deploy any repository.
- Edit .env, secrets.*, *.pem, *.key files.
- Run git push autonomously.
- Apply edits without user confirmation.

## Boundaries
- repo-scanner: read-only access to repo files.
- code-editor: write access only to files inside the target repo.
- If runtime is ambiguous, return "unknown" and list the root files
  so the host environment can decide.