# Lyzr GitAgent Orchestrator

## Overview
This repository introduces a sophisticated, multi-tiered autonomous AI worker built entirely around the open GitAgent Standard and driven by the Lyzr ADK. It functions as an intelligent software developer capable of cloning a repository, analyzing its architecture, fixing bugs, and pushing the code back to source control.

Unlike static scripts, this agent actively reasons about your codebase. It reads your project structure, determines the best approach to implement features or fix bugs, leverages the appropriate compute resources based on task complexity, and executes natively using system level tools. 

This project was developed for the Lyzr GitAgent Challenge.

## Comprehensive Capabilities

### 1. Architectural Comprehension
* **Deep Repository Scanning**: Automatically interrogates target directories to ascertain the core runtime, identify standard frameworks, locate primary entry points, and deduce required environment variables.
* **Persistent Contextual Memory**: Maintains persistent state by dynamically appending structured JSON data to a standard memory directory. This caching strategy allows subsequent agent sessions to pick up seamlessly where prior sessions left off.

### 2. Multi-Tiered Code Editing Strategy
To balance high quality output with API operational costs, the orchestrator implements a unique hierarchical routing mechanism:
* **Junior Tier**: Handles localized bugs and superficial text changes. Operates strictly within a tightly scoped logical limit.
* **Mid Tier**: Orchestrates feature additions that touch multiple files across a known module.
* **Senior Tier**: Authorized to run broad shell level structure lookups to perform large scale architectural refactoring and deep systemic debugging.

### 3. Native File System and Shell Execution
* **Direct File Manipulation**: Physically reads files to gain context and writes patches directly to your local workspace, eliminating theoretical code snippets entirely.
* **Terminal Operations**: Equipped with a secure subprocess tunnel, the orchestrator can natively run compiler checks, clone repositories, and check directory states to validate its own work before declaring a task complete.

### 4. Git Lifecycle Automation
* **Secret Management Guardrails**: Securely retrieves Personal Access Tokens (PATs) and environment variables without leaking them to the model outputs.
* **Self-Contained Commit and Push**: Autonomously handles source control operations. The agent stages modified files, generates semantically accurate commit messages, builds the secure origin URL using the hidden PAT, and pushes the resolution straight to the active branch.

## Technologies Utilized
* **Lyzr ADK**: The execution engine running the Python context window, handling the tool bindings, and powering the underlying Large Language Model logic.
* **GitAgent Standard**: The architectural foundation dictating the use of agent.yaml, SOUL.md, and structured SKILL.md files. This ensures the agent logic is fully decoupled, version controlled, and portable across platforms.

## Setup Instructions

### 1. Prerequisites
Ensure you have Python 3.8 or higher installed on your system.

### 2. Install Dependencies
Install the required packages using pip:
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create a .env file in the root directory and add your API keys:
```env
LYZR_API_KEY=your_lyzr_or_openai_key
GITHUB_PAT=your_github_personal_access_token
```

### 4. Run the Agent
Execute the main runner script to start the Lyzr ADK orchestrator loop:
```bash
python lyzr_runner.py
```

## Usage Examples
Interact with the agent using natural language prompts in the terminal:

* "Scan the repo https://github.com/example/repo, find its runtime, then use your file writing tool to save those details to runtime_report.md."
* "Ask Jnr Dev to clear out the bugs and generate the changes.md containing changed files."
* "Ask MId Dev to implement the feature request and generate the changes.md containing changed files."
* "Ask Snr Dev to refactor the codebase and generate the changes.md containing changed files."
* "Please push the changes inside my folder to GitHub. Use the commit message 'Fixed logic'."

---
*From Vivan Rajath*

