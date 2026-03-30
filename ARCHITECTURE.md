# Architecture Document

## 1. System Overview

repo-sandbox-agent is a hierarchical multi-agent system that scans Git repositories, classifies the complexity of natural language code edit requests, and delegates those edits to specialized sub-agents. The system follows the open GitAgent Standard for agent definition and composition, and is powered at runtime by the Lyzr ADK.

The core design principle is **cost-aware delegation**: simple tasks are handled by cheap, fast models while complex tasks are escalated to more capable (and more expensive) models. This is achieved through a tiered sub-agent architecture where each agent has explicitly defined permissions, tools, and scope boundaries.

## 2. Agent Hierarchy

The system contains 8 agents organized in a three-level tree:

```
repo-sandbox-agent (Orchestrator)
|
|-- repo-scanner                   Scan Orchestrator
|   |-- framework-detector         Phase 1: Manifest reading, runtime detection
|   +-- deep-scan-agent            Phase 2: Deep traversal, architecture summary
|
|-- intent-router                  Complexity classifier (skill, not a full agent)
|
+-- code-editor                    Edit Orchestrator
    |-- jnr-developer              Tier jnr: Single-file edits
    |-- snr-developer              Tier snr: Multi-file features
    +-- architect                  Tier architect: System-level changes
```

### 2.1 Orchestrator (Root)

The top-level coordinator. It receives user messages and routes them to the appropriate parent agent. It never reads or writes files directly. All file operations are delegated down the hierarchy.

**Path:** `/` (root)
**Config:** `agent.yaml`, `SOUL.md`, `DUTIES.md`, `RULES.md`, `AGENTS.md`

### 2.2 repo-scanner

A scan orchestrator that coordinates two sub-agents in sequence to produce a complete structured JSON profile of a target repository.

**Path:** `agents/repo-scanner/`
**Tools:** file-read, shell-exec (delegated to sub-agents)
**Output:** Merged JSON from both sub-agents

| Sub-Agent | Phase | Model | Tools | Produces |
|---|---|---|---|---|
| framework-detector | 1 | google:gemini-2.0-flash | file-read | runtime, version_hint, entry, install_cmd, run_cmd, port, framework |
| deep-scan-agent | 2 | anthropic:claude-sonnet-4-5-20250514 | file-read, shell-exec | file_structure, context_summary, env_vars_needed |

### 2.3 intent-router

A classification skill (not a standalone agent directory) that evaluates user instructions against the scanned codebase structure and assigns a complexity tier. This tier determines which code-editor sub-agent handles the task.

**Path:** `skills/route-intent/`
**Input:** User instruction + repo-scanner JSON
**Output:** One of `jnr`, `snr`, or `architect`

Classification logic:

| Severity | Tier | Target Sub-Agent | Indicators |
|---|---|---|---|
| Low | jnr | jnr-developer | Single-file fix, typo, style tweak, config value change |
| Medium | snr | snr-developer | Multi-file feature, component creation, route setup, integration |
| High | architect | architect | Architecture refactor, memory leak, complex debugging, system redesign |

### 2.4 code-editor

An edit orchestrator that receives a tier assignment from the intent-router and delegates the actual file editing to the matching sub-agent.

**Path:** `agents/code-editor/`
**Delegation:** Tier-based, exactly one sub-agent per task

| Sub-Agent | Tier | Model | Tools | Scope |
|---|---|---|---|---|
| jnr-developer | jnr | google:gemini-2.0-flash | file-read, file-write | Single file only |
| snr-developer | snr | anthropic:claude-sonnet-4-5-20250514 | file-read, file-write | Multi-file, within depth-3 map |
| architect | architect | anthropic:claude-sonnet-4-5-20250514 | file-read, file-write, shell-exec | Full codebase, unrestricted depth |

## 3. Request Flow

### 3.1 Scan Flow

```
User: "Scan /path/to/repo"
  |
  v
Orchestrator
  |
  v
repo-scanner
  |-- Phase 1: framework-detector
  |     Reads manifest files (package.json, requirements.txt, go.mod, etc.)
  |     Returns: runtime, framework, entry, commands, port
  |
  |-- Phase 2: deep-scan-agent
  |     Runs shell commands (tree, find, grep) for full traversal
  |     Returns: file_structure, context_summary, env_vars_needed
  |
  +-- Assembles both outputs into single JSON
      Stores result in memory/MEMORY.md
      Updates memory/runtime/context.md
```

### 3.2 Edit Flow

```
User: "Change the background color to blue"
  |
  v
Orchestrator
  |
  v
intent-router (skill)
  |  Classifies: LOW complexity
  |  Output: "jnr"
  |
  v
code-editor
  |
  v
jnr-developer
  |  Reads target file
  |  Generates minimal diff
  |  Presents diff for confirmation
  |  Writes on confirmation
  |
  v
Response to user
```

### 3.3 Combined Flow (Scan + Edit)

```
User: "Scan this repo and add a /health endpoint"
  |
  v
Orchestrator
  |
  |-- Step 1: repo-scanner (full scan)
  |     framework-detector -> deep-scan-agent -> assembled JSON
  |
  |-- Step 2: intent-router
  |     Input: "add a /health endpoint" + scan JSON
  |     Output: "snr" (multi-file route + handler)
  |
  +-- Step 3: code-editor -> snr-developer
        Reads route file + handler file
        Generates diffs for both
        Presents diffs for confirmation
        Writes on confirmation
```

## 4. GitAgent Standard Compliance

Every agent and sub-agent in the hierarchy follows the GitAgent Standard directory structure. The structure is recursive: sub-agents are nested inside their parent's `agents/` directory and follow the same file conventions.

### 4.1 Per-Agent File Manifest

| File | Purpose | Required |
|---|---|---|
| agent.yaml | Manifest: name, version, model, tools, skills, sub_agents | Yes |
| SOUL.md | Identity, personality, communication style | Yes |
| SKILL.md | Capability definition, steps, scope, guardrails | Yes |
| DUTIES.md | Segregation of duties, permissions, boundaries, escalation policy | Yes |

### 4.2 Root-Level Standard Files

| File/Directory | Purpose |
|---|---|
| agent.yaml | Root manifest with full sub_agents hierarchy |
| SOUL.md | Orchestrator identity and agent hierarchy tree |
| RULES.md | Hard constraints (must-always, must-never, safety boundaries) |
| DUTIES.md | Segregation of duties with permission matrix for all agents |
| AGENTS.md | Framework-agnostic fallback instructions, full agent documentation |
| skills/ | Reusable capability modules (detect-runtime, route-intent, apply-edit) |
| tools/ | MCP-compatible tool schemas (file-read.yaml, file-write.yaml, shell-exec.yaml) |
| workflows/ | Multi-step procedure definitions (scan-repo.yaml, edit-code.yaml) |
| knowledge/ | Reference documents agents can consult |
| memory/ | Persistent cross-session state (MEMORY.md, runtime/context.md) |
| hooks/ | Lifecycle event handlers (bootstrap.md) |
| examples/ | Few-shot calibration interactions |
| .gitagent/ | Ephemeral runtime state (gitignored) |

### 4.3 Directory Tree

```
repo-sandbox-agent/
|
|-- agent.yaml
|-- SOUL.md
|-- RULES.md
|-- DUTIES.md
|-- AGENTS.md
|
|-- agents/
|   |-- code-editor/
|   |   |-- agent.yaml
|   |   |-- SOUL.md
|   |   |-- SKILL.md
|   |   |-- DUTIES.md
|   |   +-- agents/
|   |       |-- jnr-developer/
|   |       |   |-- agent.yaml, SOUL.md, SKILL.md, DUTIES.md
|   |       |-- snr-developer/
|   |       |   |-- agent.yaml, SOUL.md, SKILL.md, DUTIES.md
|   |       +-- architect/
|   |           |-- agent.yaml, SOUL.md, SKILL.md, DUTIES.md
|   |
|   +-- repo-scanner/
|       |-- agent.yaml
|       |-- SOUL.md
|       |-- SKILL.md
|       |-- DUTIES.md
|       +-- agents/
|           |-- framework-detector/
|           |   |-- agent.yaml, SOUL.md, SKILL.md, DUTIES.md
|           +-- deep-scan-agent/
|               |-- agent.yaml, SOUL.md, SKILL.md, DUTIES.md
|
|-- skills/
|   |-- apply-edit/
|   |   |-- SKILL.md
|   |   +-- scripts/patch.py
|   |-- detect-runtime/
|   |   |-- SKILL.md
|   |   +-- scripts/detect.sh
|   +-- route-intent/
|       +-- SKILL.md
|
|-- tools/
|   |-- file-read.yaml
|   |-- file-write.yaml
|   +-- shell-exec.yaml
|
|-- workflows/
|   |-- edit-code.yaml
|   +-- scan-repo.yaml
|
|-- knowledge/
|-- memory/
|   |-- MEMORY.md
|   +-- runtime/context.md
|-- hooks/bootstrap.md
|-- examples/scan-and-edit.md
|-- .gitagent/
|
|-- lyzr_runner.py
|-- requirements.txt
+-- .gitignore
```

## 5. Tool Definitions

All tools follow MCP-compatible YAML schemas defined in the `tools/` directory. The Python runner (`lyzr_runner.py`) implements these tools as callable functions registered with the Lyzr ADK.

| Tool | Schema | Description | Access Control |
|---|---|---|---|
| file-read | tools/file-read.yaml | Read file contents at a given path | All agents |
| file-write | tools/file-write.yaml | Write content to a file (blocks .env, .pem, .key) | code-editor sub-agents only |
| shell-exec | tools/shell-exec.yaml | Execute read-only shell commands (blocks rm, install, deploy) | architect, deep-scan-agent only |
| scan_repo | (Python function) | Two-phase repo scanning with manifest detection | Orchestrator |
| route_intent | (Python function) | Keyword-based complexity classification | Orchestrator |
| get_env_var | (Python function) | Read environment variables securely | Orchestrator |
| git_push | (Python function) | Stage, commit, and push using PAT authentication | Orchestrator |

### 5.1 Safety Enforcement

The `shell_exec` tool enforces a blocklist at runtime:

```
Blocked commands: rm, del, format, mkfs, npm install, pip install,
cargo build, go build, make, docker, deploy, git push, git commit
```

The `write_file` tool blocks writes to sensitive files:

```
Blocked targets: .env, .env.local, *.pem, *.key
```

## 6. Model Assignment Strategy

Models are assigned based on the cost-complexity tradeoff:

| Agent | Model | Rationale |
|---|---|---|
| Orchestrator | anthropic:claude-sonnet-4-5-20250514 | Needs reasoning for routing decisions |
| framework-detector | google:gemini-2.0-flash | Simple pattern matching, high speed, low cost |
| deep-scan-agent | anthropic:claude-sonnet-4-5-20250514 | Needs reasoning for architecture summarization |
| jnr-developer | google:gemini-2.0-flash | Simple edits, low cost |
| snr-developer | anthropic:claude-sonnet-4-5-20250514 | Multi-file reasoning required |
| architect | anthropic:claude-sonnet-4-5-20250514 | Complex reasoning, architecture decisions |

Fallback chains are defined per agent in each `agent.yaml`. If the preferred model is unavailable, the system falls back to `openai:gpt-4o` or `openai:gpt-4o-mini` depending on the tier.

## 7. Memory and State Management

### 7.1 Persistent Memory

`memory/MEMORY.md` stores scan results across sessions. Each scan appends a timestamped JSON block, allowing the code-editor sub-agents to reference previous scan context without re-scanning.

### 7.2 Runtime Context

`memory/runtime/context.md` holds the live session state:

```
- repo: (current target repository)
- runtime: (detected runtime)
- framework: (detected framework)
- last_scan: (timestamp of last scan)
- active_agent: (currently active agent)
```

This file is overwritten on each scan. It provides quick context for the orchestrator without parsing the full MEMORY.md history.

### 7.3 Ephemeral State

`.gitagent/` holds runtime state that should not be committed. It is listed in `.gitignore`.

## 8. Workflow Definitions

Workflows are declarative YAML files that define multi-step agent procedures.

### 8.1 scan-repo.yaml

Trigger: User message matches `scan|detect|what runtime|how to run`

Steps:
1. `framework-detector` reads manifests, produces runtime fields
2. `deep-scan-agent` traverses filesystem, produces context fields
3. Merge both outputs into single JSON
4. Write result to memory/MEMORY.md
5. Return assembled JSON to user

### 8.2 edit-code.yaml

Trigger: User message matches `change|edit|add|remove|update|fix|rename|make`

Steps:
1. Load context from memory/MEMORY.md
2. Run intent-router to classify complexity and assign tier
3. Delegate to code-editor with tier assignment
4. Code-editor forwards to the matching sub-agent (jnr/snr/architect)
5. Sub-agent reads, diffs, confirms, writes
6. Return result to user

## 9. Extensibility

The architecture supports adding new agents at any level by following this pattern:

1. Create a new directory under the parent's `agents/` folder
2. Add the four standard files: `agent.yaml`, `SOUL.md`, `SKILL.md`, `DUTIES.md`
3. Update the parent's `agent.yaml` to include the new agent in `sub_agents`
4. Update the parent's `SOUL.md` to document when the new agent is delegated to

Because the `discover_sub_agents()` function in `lyzr_runner.py` recursively walks the entire `agents/` tree, newly added sub-agents are automatically discovered at startup without modifying the runner code.

## 10. Security Model

| Control | Enforcement |
|---|---|
| Sensitive file protection | write_file blocks .env, .pem, .key at runtime |
| Shell command restrictions | shell_exec blocklist prevents destructive operations |
| Scope boundaries | Each sub-agent's DUTIES.md defines permitted tools and scope |
| Escalation policy | Lower-tier agents must escalate tasks that exceed their scope |
| Secret management | PATs are read from environment, never passed to model output |
| Git push safety | Requires explicit user confirmation per RULES.md |
| Diff-before-write | All agents must show diffs before applying file changes |
