---
name: repo-scan
description: >
  Detect runtime, framework, entry point, run command, port,
  and required environment variables from a repository root.
---

## Steps

1. List root directory via shell_exec: `ls -1 <repo_path>`
2. Match files against runtime indicators (see SOUL.md order)
3. Read the matched manifest file via file_read
4. Extract: runtime, version_hint, entry, install_cmd, run_cmd,
   port, framework, env_vars_needed
5. For env_vars_needed: scan .env.example or grep for
   os.environ / process.env in the entry file
6. Return JSON only

## Output Example
```json
{
  "runtime": "python",
  "version_hint": "3.11",
  "entry": "app.py",
  "install_cmd": "pip install -r requirements.txt",
  "run_cmd": "python app.py",
  "port": 5000,
  "framework": "flask",
  "env_vars_needed": ["SECRET_KEY", "DATABASE_URL"]
}
```