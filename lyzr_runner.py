import os
import json
import yaml
import subprocess
from dotenv import load_dotenv
from lyzr import Studio


AGENT_DIR = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# GitAgent spec loader
# ---------------------------------------------------------------------------

def load_agent_spec(agent_path):
    """Reads agent.yaml + SOUL.md + DUTIES.md from a given agent directory.
    Returns (config_dict, soul_text, duties_text).
    """
    config, soul, duties = None, "", ""

    yaml_path = os.path.join(agent_path, "agent.yaml")
    if os.path.isfile(yaml_path):
        with open(yaml_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

    soul_path = os.path.join(agent_path, "SOUL.md")
    if os.path.isfile(soul_path):
        with open(soul_path, "r", encoding="utf-8") as f:
            soul = f.read()

    duties_path = os.path.join(agent_path, "DUTIES.md")
    if os.path.isfile(duties_path):
        with open(duties_path, "r", encoding="utf-8") as f:
            duties = f.read()

    return config, soul, duties


def discover_sub_agents(agent_path):
    """Recursively discover all sub-agents under agent_path/agents/.
    Returns a dict mapping agent_name -> full_path for every nested agent.
    """
    agents_dir = os.path.join(agent_path, "agents")
    registry = {}

    if not os.path.isdir(agents_dir):
        return registry

    for entry in os.listdir(agents_dir):
        sub_path = os.path.join(agents_dir, entry)
        if os.path.isdir(sub_path) and os.path.isfile(os.path.join(sub_path, "agent.yaml")):
            registry[entry] = sub_path
            # Recurse into deeper nesting
            nested = discover_sub_agents(sub_path)
            registry.update(nested)

    return registry


def load_skill(agent_path):
    """Reads SKILL.md from an agent directory."""
    skill_path = os.path.join(agent_path, "SKILL.md")
    if os.path.isfile(skill_path):
        with open(skill_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


# ---------------------------------------------------------------------------
# Tool definitions (MCP-compatible)
# ---------------------------------------------------------------------------

def scan_repo(url: str) -> str:
    """Scans the provided repository path to detect its runtime, run_cmd,
    port, and framework. Returns structured JSON."""
    print(f"\n[repo-scanner] Scanning {url} ...")

    # Phase 1: framework-detector
    print("[repo-scanner -> framework-detector] Detecting runtime & framework ...")
    framework_result = {
        "runtime": "python",
        "version_hint": "3.11",
        "entry": "app.py",
        "install_cmd": "pip install -r requirements.txt",
        "run_cmd": "python app.py",
        "port": 5000,
        "framework": "flask",
    }

    # Phase 2: deep-scan-agent
    print("[repo-scanner -> deep-scan-agent] Deep scanning file structure ...")
    deep_scan_result = {
        "file_structure": "",
        "context_summary": "",
        "env_vars_needed": [],
    }

    # Attempt real detection via shell
    try:
        tree_cmd = f'find "{url}" -maxdepth 4 -type f 2>/dev/null || dir /s /b "{url}" 2>nul'
        result = subprocess.run(tree_cmd, shell=True, capture_output=True, text=True, cwd=AGENT_DIR)
        if result.stdout.strip():
            deep_scan_result["file_structure"] = result.stdout.strip()[:2000]

        # Detect runtime from manifest files
        root_files = os.listdir(url) if os.path.isdir(url) else []

        if "package.json" in root_files:
            framework_result["runtime"] = "node"
            pkg_path = os.path.join(url, "package.json")
            with open(pkg_path, "r", encoding="utf-8") as f:
                pkg = json.load(f)
            scripts = pkg.get("scripts", {})
            framework_result["run_cmd"] = f"npm run {list(scripts.keys())[0]}" if scripts else "npm start"
            framework_result["install_cmd"] = "npm install"
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            if "next" in deps:
                framework_result["framework"] = "nextjs"
            elif "vite" in deps:
                framework_result["framework"] = "vite"
            elif "express" in deps:
                framework_result["framework"] = "express"
            elif "react-scripts" in deps:
                framework_result["framework"] = "react"

        elif "requirements.txt" in root_files or "pyproject.toml" in root_files:
            framework_result["runtime"] = "python"
            if "manage.py" in root_files:
                framework_result["framework"] = "django"
                framework_result["run_cmd"] = "python manage.py runserver"
                framework_result["port"] = 8000
            elif os.path.isfile(os.path.join(url, "requirements.txt")):
                with open(os.path.join(url, "requirements.txt"), "r") as f:
                    reqs = f.read().lower()
                if "fastapi" in reqs or "uvicorn" in reqs:
                    framework_result["framework"] = "fastapi"
                    framework_result["run_cmd"] = "uvicorn app:app --host 0.0.0.0 --port 8000"
                    framework_result["port"] = 8000
                elif "flask" in reqs:
                    framework_result["framework"] = "flask"
                    framework_result["run_cmd"] = "python app.py"
                    framework_result["port"] = 5000

        elif "go.mod" in root_files:
            framework_result["runtime"] = "go"
            framework_result["install_cmd"] = "go mod download"
            framework_result["run_cmd"] = "go run ."

        elif "Cargo.toml" in root_files:
            framework_result["runtime"] = "rust"
            framework_result["install_cmd"] = "cargo build"
            framework_result["run_cmd"] = "cargo run"

        # Env var discovery
        env_example = os.path.join(url, ".env.example")
        if os.path.isfile(env_example):
            with open(env_example, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        deep_scan_result["env_vars_needed"].append(line.split("=")[0].strip())

    except Exception as e:
        print(f"[repo-scanner] Warning: live detection failed ({e}), using defaults")

    # Assemble final output (merge both sub-agent results)
    scan_result = {**framework_result, **deep_scan_result}
    scan_result["repository"] = url
    json_output = json.dumps(scan_result, indent=2)

    # Persist to GitAgent memory
    memory_file = os.path.join(AGENT_DIR, "memory", "MEMORY.md")
    try:
        os.makedirs(os.path.dirname(memory_file), exist_ok=True)
        with open(memory_file, "a", encoding="utf-8") as mf:
            mf.write(f"\n\n### Scan Cache ({url})\n```json\n{json_output}\n```\n")
        print(f"[memory] Updated {memory_file}")
    except Exception as e:
        print(f"[memory] Warning: could not write ({e})")

    # Update runtime context
    context_file = os.path.join(AGENT_DIR, "memory", "runtime", "context.md")
    try:
        os.makedirs(os.path.dirname(context_file), exist_ok=True)
        with open(context_file, "w", encoding="utf-8") as cf:
            cf.write(f"# Runtime Context\n\n## Current Session\n")
            cf.write(f"- repo: {url}\n")
            cf.write(f"- runtime: {scan_result.get('runtime', 'unknown')}\n")
            cf.write(f"- framework: {scan_result.get('framework', 'unknown')}\n")
            cf.write(f"- last_scan: latest\n")
            cf.write(f"- active_agent: repo-scanner\n")
    except Exception:
        pass

    print(f"[repo-scanner] Scan complete. Assembled output from framework-detector + deep-scan-agent.")
    return json_output


def route_intent(instruction: str, context_summary: str) -> str:
    """Classifies the complexity of an edit instruction and returns the
    tier assignment: jnr, snr, or architect.

    Delegates to:
      jnr -> jnr-developer (single-file, low cost)
      snr -> snr-developer (multi-file, standard cost)
      architect -> architect (system-level, high cost)
    """

    instruction_lower = instruction.lower()

    # High complexity indicators -> architect
    architect_keywords = [
        "refactor", "architecture", "redesign", "memory leak", "performance",
        "optimize", "migration", "pipeline", "decompose", "restructure",
        "debug", "diagnose", "502", "500", "race condition", "deadlock",
        "connection pool", "caching layer", "microservice",
    ]
    if any(kw in instruction_lower for kw in architect_keywords):
        print("[intent-router] Complexity: HIGH -> architect sub-agent")
        return "architect"

    # Medium complexity indicators -> snr-developer
    snr_keywords = [
        "add endpoint", "add route", "create component", "new module",
        "integrate", "api", "middleware", "auth", "jwt", "database",
        "multi-file", "across files", "service", "controller",
        "create page", "add feature", "implement",
    ]
    if any(kw in instruction_lower for kw in snr_keywords):
        print("[intent-router] Complexity: MEDIUM -> snr-developer sub-agent")
        return "snr"

    # Default: low complexity -> jnr-developer
    print("[intent-router] Complexity: LOW -> jnr-developer sub-agent")
    return "jnr"


def write_file(filepath: str, content: str) -> str:
    """Writes content to a file on the disk. Used by code-editor sub-agents
    to apply edits after user confirmation."""
    try:
        # Safety: resolve relative to agent dir
        if not os.path.isabs(filepath):
            safe_path = os.path.join(AGENT_DIR, filepath)
        else:
            safe_path = filepath

        # Block writes to sensitive files (RULES.md enforcement)
        basename = os.path.basename(safe_path).lower()
        if basename in [".env", ".env.local"] or basename.endswith((".pem", ".key")):
            return f"BLOCKED: Cannot write to sensitive file '{basename}' (see RULES.md)"

        os.makedirs(os.path.dirname(safe_path), exist_ok=True)
        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[file-write] Wrote to {filepath}")
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return f"Failed to write file: {e}"


def read_file(filepath: str) -> str:
    """Reads content from a file on the disk. Available to all agents."""
    try:
        if not os.path.isabs(filepath):
            safe_path = os.path.join(AGENT_DIR, filepath)
        else:
            safe_path = filepath
        with open(safe_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Failed to read file: {e}"


def shell_exec(command: str) -> str:
    """Execute a read-only shell command. Available to architect and
    deep-scan-agent sub-agents for codebase exploration.

    RULES: Only read-only commands (ls, tree, find, grep, cat, wc).
    Never run build, install, test, or deploy commands.
    """
    # Block dangerous commands (RULES.md enforcement)
    blocked = ["rm ", "del ", "format ", "mkfs", "npm install", "pip install",
               "cargo build", "go build", "make ", "docker ", "deploy",
               "git push", "git commit"]
    cmd_lower = command.lower().strip()
    for b in blocked:
        if b in cmd_lower:
            return f"BLOCKED: '{b.strip()}' is not allowed (see RULES.md). Only read-only commands permitted."

    try:
        print(f"[shell-exec] {command}")
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            cwd=AGENT_DIR, timeout=30
        )
        if result.returncode == 0:
            return f"Command succeeded:\n{result.stdout[:3000]}"
        else:
            return f"Command failed:\n{result.stderr[:1000]}"
    except subprocess.TimeoutExpired:
        return "Command timed out (30s limit)"
    except Exception as e:
        return f"Error executing command: {e}"


def get_env_var(var_name: str) -> str:
    """Read a secret environment variable such as 'GITHUB_PAT'."""
    print(f"[secrets] Reading {var_name}")
    return os.getenv(var_name, f"Secret '{var_name}' not found in environment")


def git_push(repo_folder_name: str, commit_message: str) -> str:
    """Stages, commits, and pushes code to the repository using the PAT
    from the environment. Requires user confirmation per RULES.md."""
    pat = (os.getenv("GITHUB_PAT") or os.getenv("GITHUB_TOKEN")
           or os.getenv("PAT_TOKEN") or os.getenv("PAT"))
    if not pat:
        return "Error: No GITHUB_PAT / GITHUB_TOKEN / PAT_TOKEN found in .env"

    folder_path = os.path.join(AGENT_DIR, repo_folder_name)
    if not os.path.exists(folder_path):
        return f"Error: Folder '{repo_folder_name}' not found"

    try:
        remote_out = subprocess.run(
            "git config --get remote.origin.url",
            shell=True, capture_output=True, text=True, cwd=folder_path
        )
        url = remote_out.stdout.strip()
        if not url:
            return "Error: Could not determine remote origin URL"

        if "://" in url:
            proto, rest = url.split("://", 1)
            if "@" in rest:
                rest = rest.split("@", 1)[1]
            push_url = f"{proto}://x-access-token:{pat}@{rest}"
        else:
            return f"Error: Unsupported URL format '{url}'"

        print(f"\n[git-push] Pushing {repo_folder_name} ...")
        subprocess.run("git add .", shell=True, cwd=folder_path)
        subprocess.run(f'git commit -m "{commit_message}"', shell=True, cwd=folder_path)
        push_res = subprocess.run(
            f"git push {push_url}", shell=True,
            capture_output=True, text=True, cwd=folder_path
        )

        if push_res.returncode == 0:
            return "Successfully pushed changes to remote."
        else:
            return "Failed to push. PAT might lack permissions or branch needs specifying."
    except Exception:
        return "Error during git push."


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def main():
    load_dotenv()

    print("=" * 60)
    print("  repo-sandbox-agent  |  GitAgent Standard Runner")
    print("=" * 60)

    # Load root orchestrator spec
    config, soul, duties = load_agent_spec(AGENT_DIR)
    if not config:
        print("Error: agent.yaml not found. Run from the repository root.")
        return

    print(f"\nAgent : {config.get('name', 'Unknown')} v{config.get('version', '1.0')}")
    print(f"Model : {config.get('model', {}).get('preferred', 'default')}")

    # Discover full agent hierarchy
    agent_registry = discover_sub_agents(AGENT_DIR)
    print(f"\nAgent Hierarchy ({len(agent_registry) + 1} agents discovered):")
    print(f"  Orchestrator: {config.get('name')}")
    for name, path in sorted(agent_registry.items()):
        rel = os.path.relpath(path, AGENT_DIR)
        sub_config, _, _ = load_agent_spec(path)
        model = sub_config.get("model", {}).get("preferred", "default") if sub_config else "?"
        print(f"    {name:25s} [{model}]  ({rel})")

    # Load all sub-agent souls for context
    agent_souls = {}
    for name, path in agent_registry.items():
        _, sub_soul, sub_duties = load_agent_spec(path)
        skill = load_skill(path)
        agent_souls[name] = {
            "soul": sub_soul,
            "duties": sub_duties,
            "skill": skill,
            "path": path,
        }

    # Build orchestrator instructions with hierarchy awareness
    hierarchy_context = "\n\n## Available Sub-Agents\n"
    hierarchy_context += "You delegate tasks to these sub-agents:\n\n"
    hierarchy_context += "### Scanning (repo-scanner)\n"
    hierarchy_context += "- **framework-detector**: Fast manifest reading, runtime detection\n"
    hierarchy_context += "- **deep-scan-agent**: Deep file traversal, architecture summary\n\n"
    hierarchy_context += "### Editing (code-editor, after intent-router classifies tier)\n"
    hierarchy_context += "- **jnr-developer** (tier: jnr): Single-file edits, styling, typos\n"
    hierarchy_context += "- **snr-developer** (tier: snr): Multi-file features, refactors\n"
    hierarchy_context += "- **architect** (tier: architect): System changes, complex debug\n\n"
    hierarchy_context += "### Workflow\n"
    hierarchy_context += "1. For scan requests: use scan_repo tool\n"
    hierarchy_context += "2. For edit requests: use route_intent tool first to classify, "
    hierarchy_context += "then state which sub-agent is handling it\n"
    hierarchy_context += "3. Always show diffs before writing files\n"
    hierarchy_context += "4. Always state which sub-agent is acting\n"

    full_instructions = soul + "\n\n" + duties + "\n" + hierarchy_context

    # Initialize Lyzr Studio
    api_key = os.getenv("LYZR_API_KEY", os.getenv("OPENAI_API_KEY"))
    if not api_key:
        print("\n[WARNING] LYZR_API_KEY or OPENAI_API_KEY not found!")
        print("Export your API key: export LYZR_API_KEY='your-key'")
        return

    try:
        studio = Studio(api_key=api_key)

        agent = studio.create_agent(
            name=config.get("name", "GitAgent Orchestrator"),
            provider="gpt-4o",
            role="Hierarchical Multi-Agent Coordinator",
            goal=config.get("description", "").strip(),
            instructions=full_instructions,
        )

        # Register tools
        agent.add_tool(scan_repo)
        agent.add_tool(route_intent)
        agent.add_tool(write_file)
        agent.add_tool(read_file)
        agent.add_tool(shell_exec)
        agent.add_tool(get_env_var)
        agent.add_tool(git_push)

        print("\n--- GitAgent Initialized ---")
        print(f"Tools : scan_repo, route_intent, write_file, read_file, shell_exec, get_env_var, git_push")
        print("Type 'exit' to quit.\n")

        while True:
            try:
                user_input = input("User >> ")
                if user_input.lower().strip() in ["exit", "quit"]:
                    break

                print(f"\n[orchestrator] Processing request ...")
                response = agent.run(user_input)
                print(f"\n{config.get('name')} >> {response.response}\n")
            except KeyboardInterrupt:
                print("\nExiting.")
                break

    except Exception as e:
        print(f"\nError initializing Lyzr Agent: {e}")
        print("Ensure 'lyzr' is installed: pip install lyzr")


if __name__ == "__main__":
    main()
