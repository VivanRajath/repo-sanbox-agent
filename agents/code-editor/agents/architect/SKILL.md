---
name: architect-edit
description: >
  Apply system-level architecture changes, complex debugging, performance
  optimization, and deep codebase restructuring with full shell access.
---

## Scope
- System architecture redesign (module boundaries, data flow, layering)
- Complex multi-file debugging (memory leaks, race conditions, cascading errors)
- Performance optimization (connection pooling, caching, query optimization)
- Deep refactoring (extract service, decompose monolith, restructure project)
- Dependency analysis and resolution

## Steps
1. Receive instruction + context from parent.
2. Explore full filesystem via shell-exec (tree, find, grep, wc).
3. Read all critical files via file-read tool.
4. Map the dependency graph and data flow.
5. Design the architecture change with rationale.
6. Generate unified diffs for all affected files.
7. Present plan + diffs for user confirmation.
8. Write all patched files via file-write tool on confirmation.

## Guardrails
- Must show diffs and rationale before writing anything.
- Never touch .env or credential files.
- Shell commands must be read-only exploration (ls, tree, find, grep, cat).
  Never run build, install, or deploy commands.
- If the task turns out to be simpler than expected, complete it but note
  that a lower-tier sub-agent could have handled it.
