---
name: route-intent
description: Analyzes user query against the codebase structure and classifies complexity to assign one of three tier levels (jnr, mid, snr).
---

## Objective
To intelligently route a user's code-edit instruction to an appropriate tier Jnr, Mid, or Snr editor in order to manage LLM resource costs.

## Inputs
- User Instruction
- Repo-Scanner Output (`file_structure` and `context_summary`)

## Routing Logic
1. Evaluate instruction severity:
   - **Low**: single file fix, typo, style tweak, small isolated chunk, single logic handler. Does not require broad context.
   - **Medium**: multi-file interactions, creating a new component, basic route setup, integration tasks. Needs overview context.
   - **High**: systemic architecture refactors, resolving memory leaks, ambiguous design changes, complex bug hunting. Requires deep file structures.
2. If **Low**, assign `jnr` tier (small/flash models).
3. If **Medium**, assign `mid` tier (standard/sonnet-level models).
4. If **High**, assign `snr` tier (top-tier/opus/4o models).

## Output
Produce a single token indicating the routed tier (`jnr`, `mid`, or `snr`) and delegate the instruction + repo context to the corresponding `code-editor` instance based on the yaml configuration.
