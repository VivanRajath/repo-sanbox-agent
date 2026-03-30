---
name: route-intent
description: >
  Analyzes user query against the codebase structure and classifies
  complexity to assign one of three sub-agents (jnr-developer,
  snr-developer, architect).
---

## Objective
To intelligently route a user's code-edit instruction to the appropriate
sub-agent in order to manage LLM resource costs.

## Inputs
- User Instruction
- Repo-Scanner Output (file_structure and context_summary)

## Routing Logic
1. Evaluate instruction severity:
   - **Low**: single file fix, typo, style tweak, small isolated chunk, single logic handler. Does not require broad context.
   - **Medium**: multi-file interactions, creating a new component, basic route setup, integration tasks. Needs overview context.
   - **High**: systemic architecture refactors, resolving memory leaks, ambiguous design changes, complex bug hunting. Requires deep file structures.
2. If **Low**, delegate to **jnr-developer** (`jnr` tier, flash models).
3. If **Medium**, delegate to **snr-developer** (`snr` tier, sonnet-level models).
4. If **High**, delegate to **architect** (`architect` tier, top-tier models).

## Output
Produce a single token indicating the routed sub-agent (`jnr`, `snr`, or
`architect`) and delegate the instruction + repo context to the
code-editor, which forwards to the corresponding sub-agent.
