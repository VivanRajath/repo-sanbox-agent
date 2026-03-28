---
name: detect-runtime
description: Shell-based runtime detection and context scanning for a repository root. Returns structured JSON with framework, commands, and file structure insights.
---

## Usage
Invoked by repo-scanner agent via shell-exec tool.
Script: skills/detect-runtime/scripts/detect.sh <repo_path>

## Output
Valid JSON with fields:
- `runtime`, `version_hint`, `entry`, `install_cmd`, `run_cmd`, `port`, `framework`, `env_vars_needed`
- `file_structure`: Directory tree output (max depth 3) to prevent LLM context bloat while providing sufficient context for Editor Agents.
- `context_summary`: High-level architectural overview to orient Mid/Snr editors.

*Note:* Senior agents have leeway to query beyond the `file_structure` 3-tier limit using `shell-exec` if a deeper dive is required for architecture-level tasks.
