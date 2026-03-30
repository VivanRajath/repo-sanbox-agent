# repo-sandbox-agent

A multi-agent system built on the open GitAgent Standard and powered by the Lyzr ADK. It scans Git repositories to detect runtime environments, classifies the complexity of natural language code edit requests, and delegates those edits to tiered autonomous sub-agents. Simple tasks go to fast, cheap models. Complex tasks go to capable, expensive models. This cost-aware routing is the core design decision behind the architecture.

Developed for the Lyzr GitAgent Challenge.

## Table of Contents

- [Architecture](#architecture)
- [Agent Hierarchy](#agent-hierarchy)
- [Capabilities](#capabilities)
- [GitAgent Standard Compliance](#gitagent-standard-compliance)
- [Repository Structure](#repository-structure)
- [Setup](#setup)
- [Usage](#usage)
- [Tool Reference](#tool-reference)
- [Model Assignment](#model-assignment)
- [Security](#security)
- [Extensibility](#extensibility)

## Architecture

For the full technical architecture document, see [ARCHITECTURE.md](ARCHITECTURE.md).

The system uses a three-level agent hierarchy where parent agents act as orchestrators and leaf agents perform the actual work. All agents follow the recursive GitAgent Standard structure with `agent.yaml`, `SOUL.md`, `SKILL.md`, and `DUTIES.md`.

```
repo-sandbox-agent (Orchestrator)
|
|-- repo-scanner                   Scan Orchestrator
|   |-- framework-detector         Manifest reading, runtime detection
|   +-- deep-scan-agent            Deep traversal, architecture summary
|
|-- intent-router                  Complexity classifier
|
+-- code-editor                    Edit Orchestrator
    |-- jnr-developer              Single-file edits (low cost)
    |-- snr-developer              Multi-file features (standard cost)
    +-- architect                  System-level changes (high cost)
```

## Agent Hierarchy

### Orchestrator

The root agent. Receives user messages and routes them to either the repo-scanner (for scan requests) or the intent-router followed by the code-editor (for edit requests). It never reads, writes, or executes anything directly.

### repo-scanner

Coordinates a two-phase scan:

1. **framework-detector** reads manifest files (package.json, requirements.txt, go.mod, Cargo.toml, Gemfile, pom.xml, Dockerfile) and returns runtime, framework, version, entry point, install command, run command, and port.

2. **deep-scan-agent** uses shell commands to traverse the full directory tree, discover environment variable usage (os.environ, process.env, env.Get), and produce a structural summary of the codebase.

The parent scanner merges both outputs into a single JSON object and stores it in `memory/MEMORY.md` for use by the code-editor sub-agents.

### intent-router

A classification skill that evaluates user instructions against the scanned codebase structure. It assigns one of three complexity tiers:

| Severity | Tier | Sub-Agent | Example |
|---|---|---|---|
| Low | jnr | jnr-developer | "change the background color to red" |
| Medium | snr | snr-developer | "add a /health endpoint router and module" |
| High | architect | architect | "refactor the database layer to use connection pooling" |

### code-editor

An edit orchestrator that receives the tier from the intent-router and delegates to the matching sub-agent:

- **jnr-developer**: Handles single-file edits. Uses fast, cheap models (gemini-2.0-flash). Has file-read and file-write access only. Cannot use shell commands or make architecture decisions.

- **snr-developer**: Handles multi-file features and refactors. Uses standard models (claude-sonnet). Has file-read and file-write access. Works within the scanner's depth-3 file structure map.

- **architect**: Handles system-level architecture changes and complex debugging. Uses top-tier models (claude-sonnet with gpt-4o fallback). Has full tool access including shell-exec for deep filesystem exploration beyond the scanner's depth-3 limit.

## Capabilities

### Repository Scanning

- Automatic runtime detection across Python, Node.js, Go, Rust, Ruby, Java, and Docker
- Framework identification (Flask, FastAPI, Django, Express, Next.js, Vite, Gin, Actix, Rails, etc.)
- Deep file structure analysis with full directory tree traversal
- Environment variable discovery from source code and .env.example files
- Architecture summarization for downstream code editing context
- Persistent memory: scan results are appended to `memory/MEMORY.md` and live session state is tracked in `memory/runtime/context.md`

### Tiered Code Editing

- Three-tier sub-agent system balancing quality against API cost
- Keyword-based complexity classification for automatic tier routing
- Minimal diff generation: agents change only what was asked
- Confirmation workflow: all agents show diffs before writing
- Escalation policy: lower-tier agents report back if a task exceeds their scope

### Native System Operations

- Direct file read/write to the local filesystem
- Shell command execution with safety blocklist
- Git lifecycle automation (stage, commit, push) using PAT authentication
- Secret management with environment variable isolation

## GitAgent Standard Compliance

Every agent in the hierarchy follows the GitAgent Standard directory conventions:

| File | Purpose |
|---|---|
| agent.yaml | Manifest defining name, version, model preferences, tools, skills, and sub-agents |
| SOUL.md | Agent identity, personality, communication style, and workflow |
| SKILL.md | Capability definition with steps, scope, patterns, and guardrails |
| DUTIES.md | Segregation of duties, permissions, boundaries, and escalation policy |

Root-level standard files provide system-wide governance:

| File | Purpose |
|---|---|
| RULES.md | Hard constraints (must-always, must-never rules, safety boundaries) |
| AGENTS.md | Full agent tree documentation with I/O specifications and delegation flows |
| DUTIES.md | Orchestrator-level segregation of duties with permission matrix |

Additional standard directories:

| Directory | Purpose |
|---|---|
| skills/ | Reusable capability modules with SKILL.md definitions and helper scripts |
| tools/ | MCP-compatible tool schemas in YAML format |
| workflows/ | Declarative multi-step procedure definitions |
| knowledge/ | Reference documents available to all agents |
| memory/ | Persistent cross-session state and live runtime context |
| hooks/ | Lifecycle event handlers (bootstrap sequence) |
| examples/ | Few-shot calibration interactions for agent behavior |
| .gitagent/ | Ephemeral runtime state (gitignored) |

## Repository Structure

```
repo-sandbox-agent/
|-- agent.yaml                  Root manifest
|-- SOUL.md                     Orchestrator identity
|-- RULES.md                    Hard constraints
|-- DUTIES.md                   Segregation of duties
|-- AGENTS.md                   Full agent documentation
|-- ARCHITECTURE.md             Technical architecture document
|-- README.md                   This file
|
|-- agents/
|   |-- code-editor/
|   |   |-- agent.yaml, SOUL.md, SKILL.md, DUTIES.md
|   |   +-- agents/
|   |       |-- jnr-developer/
|   |       |   +-- agent.yaml, SOUL.md, SKILL.md, DUTIES.md
|   |       |-- snr-developer/
|   |       |   +-- agent.yaml, SOUL.md, SKILL.md, DUTIES.md
|   |       +-- architect/
|   |           +-- agent.yaml, SOUL.md, SKILL.md, DUTIES.md
|   +-- repo-scanner/
|       |-- agent.yaml, SOUL.md, SKILL.md, DUTIES.md
|       +-- agents/
|           |-- framework-detector/
|           |   +-- agent.yaml, SOUL.md, SKILL.md, DUTIES.md
|           +-- deep-scan-agent/
|               +-- agent.yaml, SOUL.md, SKILL.md, DUTIES.md
|
|-- skills/
|   |-- apply-edit/             Code editing skill with patch script
|   |-- detect-runtime/         Runtime detection skill with shell script
|   +-- route-intent/           Complexity classification skill
|
|-- tools/                      MCP-compatible tool schemas
|-- workflows/                  Declarative multi-step procedures
|-- knowledge/                  Reference documents
|-- memory/                     Persistent state and runtime context
|-- hooks/                      Lifecycle handlers
|-- examples/                   Few-shot calibration
|-- .gitagent/                  Runtime state (gitignored)
|
|-- lyzr_runner.py              Lyzr ADK runner (main entry point)
|-- requirements.txt            Python dependencies
+-- .gitignore
```

## Setup

### Prerequisites

- Python 3.8 or higher
- A Lyzr API key or OpenAI API key
- A GitHub Personal Access Token (for git push functionality)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment

Create a `.env` file in the repository root:

```env
LYZR_API_KEY=your_lyzr_or_openai_api_key
GITHUB_PAT=your_github_personal_access_token
```

### Run the Agent

```bash
python lyzr_runner.py
```

On startup, the runner will:
1. Load the root `agent.yaml` and `SOUL.md`
2. Recursively discover all sub-agents in the `agents/` tree
3. Print the full agent hierarchy with model assignments
4. Register all tools with the Lyzr ADK
5. Enter the interactive prompt

Example startup output:

```
============================================================
  repo-sandbox-agent  |  GitAgent Standard Runner
============================================================

Agent : repo-sandbox-agent v1.0.0
Model : anthropic:claude-sonnet-4-5-20250514

Agent Hierarchy (8 agents discovered):
  Orchestrator: repo-sandbox-agent
    architect                 [anthropic:claude-sonnet-4-5-20250514]
    code-editor               [anthropic:claude-sonnet-4-5-20250514]
    deep-scan-agent           [anthropic:claude-sonnet-4-5-20250514]
    framework-detector        [google:gemini-2.0-flash]
    jnr-developer             [google:gemini-2.0-flash]
    repo-scanner              [anthropic:claude-sonnet-4-5-20250514]
    snr-developer             [anthropic:claude-sonnet-4-5-20250514]

--- GitAgent Initialized ---
Tools : scan_repo, route_intent, write_file, read_file, shell_exec, get_env_var, git_push
Type 'exit' to quit.
```

## Usage

Interact with the agent using natural language prompts in the terminal.

### Scanning a Repository

```
User >> Scan /path/to/my-project and tell me the runtime
```

The orchestrator will delegate to repo-scanner, which runs framework-detector then deep-scan-agent, and returns the assembled JSON.

### Code Editing (Automatic Tier Routing)

```
User >> Change the background color in style.css to dark blue
```

The intent-router classifies this as LOW complexity and routes to jnr-developer, which reads the file, generates a diff, and writes on confirmation.

```
User >> Add a /health endpoint with a JSON response
```

Classified as MEDIUM complexity, routed to snr-developer.

```
User >> Refactor the database layer to use connection pooling and fix the memory leak
```

Classified as HIGH complexity, routed to architect.

### Combined Scan and Edit

```
User >> Scan https://github.com/user/repo, then add a login page
```

The orchestrator runs the scan first, stores context, then routes the edit through intent-router to the appropriate sub-agent.

### Git Operations

```
User >> Push the changes in my-project to GitHub with commit message "Fixed routing bug"
```

The orchestrator uses the git_push tool with PAT authentication from the environment.

## Tool Reference

| Tool | Description | Available To |
|---|---|---|
| scan_repo | Two-phase repo scanning (framework-detector then deep-scan-agent) | Orchestrator |
| route_intent | Keyword-based complexity classification returning jnr/snr/architect | Orchestrator |
| read_file | Read file contents at a given path | All agents |
| write_file | Write content to a file (blocks .env, .pem, .key) | code-editor sub-agents |
| shell_exec | Execute read-only shell commands (blocks destructive operations) | architect, deep-scan-agent |
| get_env_var | Read environment variables securely | Orchestrator |
| git_push | Stage, commit, push using PAT authentication | Orchestrator |

## Model Assignment

Models are assigned per agent based on the cost-complexity tradeoff:

| Agent | Preferred Model | Fallback | Rationale |
|---|---|---|---|
| Orchestrator | claude-sonnet-4-5 | gpt-4o, gemini-2.0-flash | Routing requires reasoning |
| framework-detector | gemini-2.0-flash | gpt-4o-mini | Simple pattern matching |
| deep-scan-agent | claude-sonnet-4-5 | gpt-4o | Architecture summarization needs reasoning |
| jnr-developer | gemini-2.0-flash | gpt-4o-mini | Simple edits, optimize for cost |
| snr-developer | claude-sonnet-4-5 | gpt-4o | Multi-file edits need reasoning |
| architect | claude-sonnet-4-5 | gpt-4o | Complex system-level reasoning |

## Security

| Control | Implementation |
|---|---|
| Sensitive file protection | write_file blocks .env, .env.local, .pem, .key at runtime |
| Shell command restrictions | shell_exec blocklist prevents rm, del, format, install, build, deploy, docker, git push, git commit |
| Scope boundaries | Each sub-agent's DUTIES.md defines permitted tools, file scope, and escalation policy |
| Secret management | PATs and API keys read from environment variables, never passed to model output |
| Diff-before-write | All agents must show unified diffs and receive confirmation before writing files |
| Git push safety | Requires explicit user instruction; PAT is injected into URL at runtime and never logged |
| Command timeout | Shell commands are limited to 30 seconds to prevent hung processes |

## Extensibility

To add a new sub-agent at any level:

1. Create a directory under the parent's `agents/` folder:
   ```
   agents/code-editor/agents/my-new-agent/
   ```

2. Add the four standard files:
   ```
   agent.yaml    - Manifest (name, model, tools, skills)
   SOUL.md       - Identity and workflow
   SKILL.md      - Capability definition and guardrails
   DUTIES.md     - Permissions and escalation policy
   ```

3. Update the parent's `agent.yaml` to include the new agent in `sub_agents`.

4. Update the parent's `SOUL.md` to document when the new agent is delegated to.

The `discover_sub_agents()` function in `lyzr_runner.py` recursively walks the entire `agents/` tree at startup, so newly added agents are automatically discovered without modifying the runner code.

---

Built by Vivan Rajath for the Lyzr GitAgent Challenge.
