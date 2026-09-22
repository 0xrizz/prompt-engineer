# Central Prompt Engineering Studio & Hub (Claude Code Instructions)

Welcome to the Prompt Engineering Hub for `/home/rizz/dev/`.

## Tooling & Commands
Always execute tools within the managed virtual environment via `uv run`:
- Fast offline unit tests: `uv run pytest tests/`
- Lint & format: `uv run ruff check .` and `uv run ruff format .`
- Multi-repo scan: `uv run prompt-eng scan`
- Transcript ingestion: `uv run prompt-eng transcript --repo <name>`
- Rubric scoring: `uv run prompt-eng score "<prompt>"`
- Diff comparison: `uv run prompt-eng diff <before> <after>`
- Catalog search: `uv run prompt-eng search <query>`

## Skill Shadowing
- For `prompt-architect`, use the local workspace skill in `.claude/skills/prompt-architect/SKILL.md`.
