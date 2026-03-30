# Example: Scan and Edit Flow

A complete interaction showing the full agent delegation chain.

## User Input
```
Scan /home/user/projects/my-flask-app and change the background color to dark blue.
```

## Step 1: Orchestrator routes to repo-scanner

The orchestrator detects both a repo path and an edit instruction.
It runs the scan first.

## Step 2: repo-scanner delegates to framework-detector

**framework-detector output:**
```json
{
  "runtime": "python",
  "version_hint": "3.11",
  "entry": "app.py",
  "install_cmd": "pip install -r requirements.txt",
  "run_cmd": "python app.py",
  "port": 5000,
  "framework": "flask"
}
```

## Step 3: repo-scanner delegates to deep-scan-agent

**deep-scan-agent output:**
```json
{
  "file_structure": "app.py\nstatic/\n  css/\n    style.css\n  js/\n    main.js\ntemplates/\n  index.html\n  base.html\nrequirements.txt",
  "context_summary": "Flask app with Jinja2 templates. Static CSS in static/css/style.css. Single-page app with base template layout.",
  "env_vars_needed": ["SECRET_KEY"]
}
```

## Step 4: repo-scanner assembles and returns full JSON

The parent merges both outputs into the complete scan result and stores
it in `memory/MEMORY.md`.

## Step 5: Orchestrator routes edit to intent-router

**intent-router input:** "change the background color to dark blue" + scan JSON
**intent-router output:** `jnr` (single CSS property change)

## Step 6: code-editor delegates to jnr-developer

**jnr-developer reads:** `static/css/style.css`
**jnr-developer output:**
```diff
--- a/static/css/style.css
+++ b/static/css/style.css
@@ -1,3 +1,3 @@
 body {
-  background-color: #ffffff;
+  background-color: #1a1a2e;
   font-family: sans-serif;
 }
```

## Step 7: User confirms, jnr-developer writes

File patched. Flow complete.
