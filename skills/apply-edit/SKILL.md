---
name: apply-edit
description: Tiered agent implementation for applying targeted edits based on a user instruction. Employs Jnr, Mid, or Snr tier logic dynamically.
---

## Role Assignment
Triggered by the `intent-router`. Handled by a specific model (`jnr`, `mid`, `snr`) defined in `agent.yaml`.

## Steps
1. Review the `repo-scanner` structured JSON to orient with `file_structure` and `context_summary`.
2. Receive parsed instruction and target file paths.
3. Read target files via `file-read` tool.
4. Generate a precise, minimal patch.
5. Show a unified diff to the user.
6. Write the patch on confirmation via `file-write` tool.

## Constraints & Guardrails
- **All Tiers**: Never touch `.env` files. If ambiguous files, list candidates and ask.
- **Jnr & Mid Tiers**: Adhere strictly to the scanner's depth 3 `file_structure` map. Do not perform heavy exploratory shell lookups. Focus locally.
- **Snr Tier (`snr` model only)**: Allowed to query deeper filesystem trees using `shell-exec` (e.g., `ls -R` / `tree`) if necessary to restructure complex codebases. Permitted to refactor architecture.

## Post-Edit
Confirm success and yield execution flow.
