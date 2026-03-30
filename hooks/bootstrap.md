# Bootstrap Hook

Startup sequence executed when the agent system initializes.

## Steps

1. **Load Memory**
   - Read `memory/MEMORY.md` for previous session context.
   - Read `memory/runtime/context.md` for live state.

2. **Validate Agent Tree**
   - Confirm all sub-agent directories exist under `agents/`.
   - Verify each sub-agent has: `agent.yaml`, `SOUL.md`, `SKILL.md`, `DUTIES.md`.
   - Recursively check nested sub-agents.

3. **Confirm Tool Availability**
   - Verify `file-read`, `file-write`, `shell-exec` tools are accessible.
   - Check tool schemas in `tools/` directory.

4. **Load Skills**
   - Read all `SKILL.md` files from `skills/` directory.
   - Confirm skill names match those referenced in `agent.yaml`.

5. **Ready State**
   - Log initialization complete to `memory/runtime/context.md`.
   - Await user input.
