---
name: apply-edit
description: >
  Tiered agent implementation for applying targeted edits based on a
  user instruction. Delegates to jnr-developer, snr-developer, or
  architect sub-agent based on intent-router tier assignment.
---

## Role Assignment
Triggered by the intent-router. The code-editor parent delegates to
the matching sub-agent:
- `jnr` tier -> jnr-developer sub-agent
- `snr` tier -> snr-developer sub-agent
- `architect` tier -> architect sub-agent

## Steps
1. Review the repo-scanner structured JSON to orient with file_structure and context_summary.
2. Receive parsed instruction and target file paths.
3. Read target files via file-read tool.
4. Generate a precise, minimal patch.
5. Show a unified diff to the user.
6. Write the patch on confirmation via file-write tool.

## Constraints & Guardrails
- **All Sub-Agents**: Never touch .env files. If ambiguous files, list candidates and ask.
- **jnr-developer**: Single-file scope only. No shell access. No architecture decisions.
- **snr-developer**: Multi-file scope within scanner's depth-3 file_structure map. No shell access.
- **architect**: Full codebase scope. Allowed to use shell-exec (read-only: ls, tree, find, grep) for deep exploration beyond depth-3 limits. Permitted to refactor architecture.

## Post-Edit
Confirm success and yield execution flow.
