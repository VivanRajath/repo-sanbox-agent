# Lyzr GitAgent Orchestrator

This repository is a multi-agent workspace built natively on the **GitAgent Standard** and orchestrated by the **Lyzr ADK**. It transforms standard Git repositories into intelligent, multi-agent tools capable of analyzing architecture, resolving bugs, and natively executing Git lifecycles.

##  What is GitAgent?
[GitAgent](https://github.com/open-gitagent/gitagent) is an open standard that fundamentally re-imagines how AI agents are defined and deployed. Instead of locking agent logic inside proprietary platforms or complex Python codebases, GitAgent stores an agent's entire brain, ruleset, and memory natively inside standard Git repositories using plain text files. 

### Core Specifications
GitAgent relies on three primary pillars situated at the root of a project:
1. **`agent.yaml`**: The technical configuration. It defines the agent's name, description, assigned tools (e.g., `file-read`, `shell-exec`), and sub-agents.
2. **`SOUL.md`**: The agent's identity and system prompt. It dictates behavioral guidelines, constraints (What the agent should NEVER do), and formatting rules.
3. **`SKILL.md` (Optional)**: Specific instructional workflows teaching the agent how to accomplish complex repeatable tasks step-by-step.
4. **`memory/`**: A persistent markdown directory where agents dump contextual state so they can pick up exactly where they left off across different sessions.

##  Gitagent Versatility
By adopting the GitAgent standard, we were able to completely decouple our agent's **behavior** from our agent's **execution engine**. 

Specifically:
- **Hierarchical Design:** We easily defined a multi-agent system (`code-editor` and `repo-scanner`) inside nested `agents/` directories simply by dropping new `agent.yaml` files.
- **Portability:** Because our system prompt and constraints live in `SOUL.md`, we didn't have to write giant LLM chains in Python. The Lyzr ADK runner simply reads the markdown files and dynamically initializes the agent.
- **Standardized Memory:** Our scanning tool natively appends JSON repository structural data to `memory/MEMORY.md`. The code-editing agent then reads that standard file to understand the environment without having to re-scan. 

## 🛠 Lyzr ADK Integration Tools
The `lyzr_runner.py` hooks the Lyzr `gpt-4o` agent directly into your machine using physical Python tools that execute the GitAgent specs:
* `scan_repo(url)`: Extracts runtime environments (Python, Node, etc.).
* `shell_exec(cmd)`: Subprocess tunneling allowing the agent to effectively run clones and compilations.
* `read_file(path)` & `write_file(path, content)`: Allows the AI to physically save bug reports.
* `get_env_var(name)` & `git_push(...)`: Natively automates authenticated Git pushes.

## 🚀 Setup & Execution

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the root directory:
```env
LYZR_API_KEY=your-lyzr-or-openai-key
GITHUB_PAT=your-github-personal-access-token
```

### 3. Run the AI Developer
```bash
python lyzr_runner.py
```

### 4. Example Prompts
You can interact with the agent using natural language prompts. For example:
> *"Scan the repo https://github.com/VivanRajath/sandbox-test, find its runtime, then use your file writing tool to save those details to runtime_report.md."*

> *"Please push the changes inside my sandbox-test folder to GitHub. Use the commit message 'Fixed logic in server.js'."*

---
*Built for the Lyzr GitAgent Challenge*