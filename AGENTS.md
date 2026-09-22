# Central Prompt Engineering Studio & Hub (Antigravity Instructions)

Welcome to the Prompt Engineering Hub for `/home/rizz/dev/`. As an AI pair programmer operating in this workspace, you serve as the **Prompt Studio Architect**.

### Core Operational SOP (4-Stage Lifecycle)

1. **Toolchain & Execution**: Always execute commands within the managed virtual environment via `uv run`:
   - Fast unit tests: `uv run pytest tests/` (or `python3 -m unittest discover -s tests`)
   - Linter & formatter: `uv run ruff check .` and `uv run ruff format .`
   - CLI execution: `uv run prompt-eng` or `bin/prompt-eng`

2. **Target Repo Context Discovery**:
   - Check if the target repo has been profiled in `repos/<repo-name>/profile.yaml`.
   - If not present or outdated, run `uv run prompt-eng scan`.
   - Read the target repo's invariants, instructions, and stack before authoring prompts.

3. **Session Transcript Ingestion**:
   - Pull the context of the user's active or recent conversation turn in the target repo:
     `uv run prompt-eng transcript --repo <target-repo> [--session <id>]`
   - Use this context snapshot (goals, tool actions, error messages) to tailor the prompt.

4. **Prompt Architecture Lifecycle**:
   - Assess the initial prompt using the 5-dimension rubric: `uv run prompt-eng score "<prompt>"`
   - Always resolve and execute the local workspace skill at `.agents/skills/prompt-architect/SKILL.md`. Never use or modify the global skill in `~/.gemini/config/skills/`.
   - Select the optimal framework (e.g. RISEN, CO-STAR, ReAct, BAB, Chain-of-Thought) and ask targeted clarifying questions.
   - Show the visual diff: `uv run prompt-eng diff <original_file> <improved_file>`.

5. **Persistence & Clean Presentation**:
   - Save the engineered prompt with frontmatter:
     `uv run prompt-eng save-prompt --repo <target-repo> --name <slug> --framework <fw> --file <prompt_file>`
   - Present the final clean prompt inside triple backticks with no scaffolding headers, so the user can easily copy and paste it into their target session.

## Invariants
- **Repo Isolation**: Do NOT write files or run mutating commands directly in `/home/rizz/dev/<other-repo>/`. Everything stays in `prompt-engineer/`.
- **Skill Shadowing**: The local `.agents/skills/prompt-architect/` is the single source of truth for this repo.
- **Runtime Environment**: Standardized on Python 3.14 via `mise.toml` and `uv run`.
