---
name: detect-runtime
description: >
  Shell-based runtime detection and context scanning for a repository root.
  Delegates to framework-detector for manifest parsing and deep-scan-agent
  for full codebase analysis. Returns structured JSON.
---

## Usage
Invoked by repo-scanner agent. Scanning is split across two sub-agents:

1. **framework-detector** (Phase 1): Reads manifest files via file-read.
   Produces runtime, version_hint, entry, install_cmd, run_cmd, port, framework.

2. **deep-scan-agent** (Phase 2): Uses shell-exec for deep traversal.
   Produces file_structure, context_summary, env_vars_needed.

Script fallback: skills/detect-runtime/scripts/detect.sh <repo_path>

## Output
Valid JSON with fields:
- runtime, version_hint, entry, install_cmd, run_cmd, port, framework, env_vars_needed
- file_structure: Directory tree output from deep-scan-agent
- context_summary: High-level architectural overview from deep-scan-agent

Note: The architect sub-agent has leeway to query beyond the file_structure
depth limit using shell-exec if a deeper dive is required for architecture-level tasks.
