# 🏛️ Prompt Engineer Hub & Studio

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Author: 0xrizz](https://img.shields.io/badge/author-0xrizz-orange.svg)](https://github.com/0xrizz)

A centralized studio and multi-repository prompt engineering platform designed to profile repositories, scaffold context-grounded prompts, enforce invariant and framework linting, extract transcript context, and catalog reusable prompt architectures across agent harnesses (Antigravity CLI, Antigravity IDE, and Claude Code).

---

## 🌟 Key Capabilities

- **Automated Repository Profiling**: Detects tech stacks (Python, Node/TS, Rust, Go), package managers (`uv`, `pnpm`, `cargo`), test runners (`pytest`, `jest`, `vitest`), linters (`ruff`, `eslint`), active skills, rules, and invariants from `AGENTS.md` and `CLAUDE.md`.
- **Grounded Prompt Scaffolding**: Generates framework-structured prompts (RISEN, CO-STAR, BAB, ReAct) pre-populated with repository invariants, test toolchains, and active milestone contexts.
- **Invariant & Framework Linting**: Validates prompts against repository invariants (e.g., package hallucination, test runner mismatches) and structural completeness with optional strict mode (`--strict`).
- **Multi-Harness Transcript Extraction**: Ingests, sanitizes, and summarizes active agent sessions (Antigravity and Claude Code) into token-efficient snapshots containing user goals, tools executed, and runtime errors.
- **Rubric Scoring & Diff Engine**: Evaluates prompts across 5 core dimensions (Clarity, Specificity, Context, Completeness, Structure) with a colored diff visualizer.
- **Searchable Prompt Catalog**: Full-text and structured catalog search with filters by repository, framework, minimum rubric score, and JSON output formatting.
- **Local Skill Shadowing**: Embeds `.agents/skills/prompt-architect/` and `.claude/skills/prompt-architect/` locally so adjustments remain isolated within the studio without mutating global configuration.

---

## 🚀 Quickstart

### Prerequisites

- Python 3.14+
- [`uv`](https://github.com/astral-sh/uv) package manager

### Installation

```bash
git clone https://github.com/0xrizz/prompt-engineer.git
cd prompt-engineer
uv sync
```

### Quick Walkthrough

```bash
# 1. Profile workspaces under development root
uv run prompt-eng scan

# 2. Inspect a target repository's profile
uv run prompt-eng profile example-repo

# 3. Scaffold a grounded prompt template (e.g. RISEN)
uv run prompt-eng scaffold --repo example-repo --name auth-middleware --framework RISEN

# 4. Lint prompt against repository invariants
uv run prompt-eng lint repos/example-repo/prompts/auth-middleware.md --repo example-repo

# 5. Score prompt quality across the 5-dimension rubric
uv run prompt-eng score "Implement bearer auth middleware adhering to zero external runtime dependencies"

# 6. Extract session summary from active conversation
uv run prompt-eng transcript --repo example-repo
```

---

## 🛠️ CLI Reference

All commands can be invoked via `uv run prompt-eng <command>` or direct executable `bin/prompt-eng <command>`.

### 1. `scan`
Scan workspace directories to generate `repos/<name>/profile.yaml` profiles.
```bash
uv run prompt-eng scan [--root /path/to/workspaces]
```

### 2. `profile`
Display the cached technical profile and invariants of a target repository.
```bash
uv run prompt-eng profile <repo-name>
```

### 3. `scaffold`
Generate framework-compliant prompt templates pre-grounded with the target repository's stack, test commands, and invariants.
```bash
uv run prompt-eng scaffold --repo <repo> --name <slug> [--framework RISEN|CO-STAR|BAB|ReAct] [--stdout]
```

### 4. `lint`
Validate prompt text or files against repository invariants, toolchain consistency, and framework structure.
```bash
uv run prompt-eng lint <path-or-text> --repo <repo> [--framework RISEN] [--strict]
```
- Returns exit code `0` on clean pass.
- Returns exit code `1` when errors are detected (or warnings when `--strict` is enabled).

### 5. `score`
Evaluate any raw or drafted prompt using the 5-dimension rubric (Clarity, Specificity, Context, Completeness, Structure).
```bash
uv run prompt-eng score "<prompt text>"
uv run prompt-eng score --file path/to/prompt.md
```

### 6. `diff`
Render an ANSI terminal visual diff between original and improved prompt versions.
```bash
uv run prompt-eng diff <original_file> <improved_file>
```

### 7. `transcript`
Extract clean, XML-sanitized session summaries from Antigravity and Claude Code conversation logs.
```bash
uv run prompt-eng transcript --repo <repo> [--session <session_id>] [--format md|json]
```

### 8. `save-prompt`
Persist an engineered prompt into `repos/<repo>/prompts/` with standardized YAML frontmatter.
```bash
uv run prompt-eng save-prompt --repo <repo> --name <slug> --framework <framework> --file <path>
```

### 9. `list`
List all engineered prompts across all tracked repository prompt directories.
```bash
uv run prompt-eng list
```

### 10. `search`
Search prompt catalog using keyword matching or structured filters, with optional JSON output.
```bash
uv run prompt-eng search "<query>" [--repo <repo>] [--framework <framework>] [--min-score 7.5] [--json]
```

---

## 🏗️ Architecture

```
prompt-engineer/
├── .agents/
│   └── skills/
│       └── prompt-architect/     # Embedded local Antigravity skill
├── .claude/
│   └── skills/
│       └── prompt-architect/     # Embedded local Claude Code skill
├── bin/
│   └── prompt-eng                # Standalone CLI entrypoint
├── prompt_eng/
│   ├── cli.py                    # Unified CLI command dispatcher
│   ├── models.py                 # Core domain models (RepoProfile, RubricScore, LintReport)
│   ├── scanner.py                # Workspace profiler and invariant extractor
│   ├── studio/
│   │   ├── catalog.py            # Prompt search and filtering engine
│   │   ├── diff.py               # Visual terminal diff utility
│   │   ├── linter.py             # Prompt invariant and structure validator
│   │   ├── scaffolder.py         # Grounded prompt template generator
│   │   └── scorer.py             # 5-dimension heuristic rubric evaluator
│   └── transcripts/
│       ├── antigravity.py        # Antigravity session parser and XML sanitizer
│       ├── claude.py             # Claude Code transcript parser
│       └── resolver.py           # Multi-repo session locator
├── repos/
│   ├── .gitkeep
│   └── example-repo/
│       └── profile.yaml          # Public reference profile
└── tests/                        # Comprehensive unit and integration test suite
```

---

## 🧪 Testing & Code Quality

The test suite runs entirely offline with zero external network or database dependencies:

```bash
# Run full unit & integration test suite
uv run pytest tests/ -v

# Run linter
uv run ruff check .

# Run formatter check
uv run ruff format --check .
```

---

## 📄 License & Attribution

- **License**: Released under the [MIT License](LICENSE). Copyright (c) 2026 **0xrizz**.
- **Skill Engine**: Prompt Architect skill engine authored and maintained by **0xrizz**.
