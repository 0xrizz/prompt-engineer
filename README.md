# 🏛️ Prompt Engineer Hub & Studio

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Version: 4.0.0](https://img.shields.io/badge/version-4.0.0-purple.svg)](https://github.com/0xrizz/prompt-engineer)
[![Author: 0xrizz](https://img.shields.io/badge/author-0xrizz-orange.svg)](https://github.com/0xrizz)

A centralized studio and multi-repository prompt engineering platform designed to profile repositories, scaffold context-grounded prompts, enforce invariant and cognitive linting, extract transcript context, and catalog reusable prompt architectures across agent harnesses (Antigravity CLI, Antigravity IDE, and Claude Code).

Powered by the **Prompt Architect v4.0.0** engine with 35 SOTA prompting frameworks, Attention & Cognitive Dynamics (Sandwich 10-80-10 & Contrastive Positive Steering), and automated multi-repo profiling.

---

## 🌟 Key Capabilities

- **Automated Repository Profiling**: Detects tech stacks (Python, Node/TS, Rust, Go), package managers (`uv`, `pnpm`, `cargo`), test runners (`pytest`, `jest`, `vitest`), linters (`ruff`, `eslint`), active skills, rules, and invariants from `AGENTS.md` and `CLAUDE.md`.
- **Grounded Prompt Scaffolding**: Generates framework-structured prompts pre-populated with repository invariants, test toolchains, and active milestone contexts across 35 frameworks including Graph-of-Thoughts (GoT), Meta-Prompting, Buffer-of-Thoughts (BoT), Medprompt, and Web Architecture contracts (`web-accessible`, `defensive-action`).
- **Invariant & Cognitive Linting**: Validates prompts against repository invariants (toolchain mismatches, package hallucinations), structural completeness, and cognitive dynamics (`WARN-SANDWICH-STRUCTURE`, `WARN-NAIVE-NEGATION`, `WARN-CLIENT-SECRET-LEAK`) with optional strict mode (`--strict`).
- **Multi-Harness Transcript Extraction**: Ingests, sanitizes, and summarizes active agent sessions (Antigravity and Claude Code) into token-efficient snapshots containing user goals, tools executed, and runtime errors.
- **6-Dimension Rubric Scoring & Diff Engine**: Evaluates prompts across 6 core dimensions (Clarity, Specificity, Context, Completeness, Structure, and Attention & Cognitive Dynamics) with a colored diff visualizer.
- **Searchable Prompt Catalog**: Full-text and structured catalog search with filters by repository, framework, minimum rubric score, and JSON output formatting.
- **Local Skill Shadowing**: Embeds `.agents/skills/prompt-architect/` and `.claude/skills/prompt-architect/` locally (v4.0.0) so adjustments remain isolated within the studio without mutating global configuration.

---

## 🧠 Scientific Prompt Engineering (v4.0.0)

Version `4.0.0` introduces scientific prompt engineering foundations rooted in cognitive attention dynamics and state-of-the-art reasoning architectures:

### 35 Frameworks Catalog Across 7 Intent Categories

The studio categorizes 35 prompting frameworks into 7 distinct operational intents:

| Intent Category | Primary Purpose | Frameworks |
|---|---|---|
| **CREATE** | Generate new content or architecture from scratch | **APE**, **RTF**, **CTF**, **RACE**, **CRISPE**, **BROKE**, **CARE**, **TIDD-EC**, **CO-STAR**, **RISEN**, **RISE-IE**, **RISE-IX**, **Graph-of-Thoughts (GoT)** |
| **TRANSFORM** | Rewrite, compress, or structurally convert existing artifacts | **BAB**, **Self-Refine**, **Chain of Density**, **Iterative Compression**, **Skeleton of Thought**, **Buffer-of-Thoughts (BoT)** |
| **REASON** | High-complexity problem solving, algorithmic reasoning, & logic | **Plan-and-Solve (PS+)**, **Least-to-Most**, **Step-Back**, **Tree of Thought**, **RCoT**, **Chain of Thought**, **Self-Consistency**, **Graph-of-Thoughts (GoT)**, **Meta-Prompting**, **Buffer-of-Thoughts (BoT)**, **Medprompt** |
| **CRITIQUE** | Stress-testing, boundary verification, & failure mode analysis | **Self-Refine**, **CAI Critique-Revise**, **Devil's Advocate**, **Pre-Mortem**, **RCoT**, **Chain-of-Verification** |
| **RECOVER** | Reconstruct prompts from high-quality target outputs | **RPEF** (Reverse Prompt Engineering) |
| **CLARIFY** | Structured requirements discovery before execution | **Reverse Role Prompting** (AI-Led Interview), **Medprompt** |
| **AGENTIC** | Autonomous tool use, iterative reasoning, & specialist orchestration | **ReAct** (Reasoning + Acting), **Meta-Prompting** |

#### Highlighted SOTA Frameworks
- **Graph-of-Thoughts (GoT)**: Models problem solving as an arbitrary Directed Acyclic Graph (DAG) of thoughts, enabling multi-branch generation nodes, score-based aggregation, and iterative refinement loops.
- **Meta-Prompting**: Central Conductor orchestrates complex tasks by decomposing them into mutually exclusive subtasks dispatched to fresh, isolated specialist agent contexts.
- **Buffer-of-Thoughts (BoT)**: Retrieves and instantiates distilled meta-thought templates from an archetype buffer, ensuring structured problem solving without ad-hoc trial-and-error.
- **Medprompt**: Combines dynamic few-shot exemplar retrieval, Chain-of-Thought reasoning steps, and choice-shuffle ensembling to eliminate positional bias.
- **Web Architecture Contracts**: Specialized scaffolding templates for WCAG 2.2 AA accessibility (`web-accessible`) and secure server action boundaries (`defensive-action`).

---

### Attention & Cognitive Dynamics (6-Dimension Rubric)

Long-context LLMs suffer from the *Lost-in-the-Middle* phenomenon, where information in the middle of long prompts receives significantly less attention weight than information at the edges. The v4.0.0 rubric and linter formally enforce:

1. **Sandwich Architecture (10-80-10 Rule)**:
   - **Head Anchor (Primacy 10%)**: Immediate role assignment, persona, and core objective (`## Role`, `## Context`, `You are...`).
   - **Body Context (Passive 80%)**: Reference code, schemas, and background documentation.
   - **Tail Anchor (Recency 10%)**: Output constraints, return format, validation steps, and narrowing criteria placed immediately prior to execution (`## Expectation`, `## Output`, `Return...`).
2. **Contrastive Positive Steering**:
   - Replaces fragile negative prohibitions (e.g., clusters of "do not", "never", "cannot") with positive behavioral guardrails (e.g., "must use", "ensure", "exclusively").

#### 6 Evaluation Dimensions

| Dimension | Description | Target Standard |
|---|---|---|
| **Clarity** | Unambiguous goals; penalizes vague words (`thing`, `stuff`, `maybe`) | Score $\ge 7$ |
| **Specificity** | Concrete criteria, types, numbers, schemas, and formats | Score $\ge 7$ |
| **Context** | Background setting, repo stack, and explicit rationale (`because`, `in order to`) | Score $\ge 7$ |
| **Completeness** | Covers role, task, steps, expectations, and failure gates | Score $\ge 7$ |
| **Structure** | Organized sections, markdown headers, and clean lists | Score $\ge 7$ |
| **Attention & Cognitive Dynamics** | Sandwich 10-80-10 anchors and contrastive positive steering | Score $\ge 7$ |

---

### Cognitive & Boundary Linter Rules

The prompt linter enforces repository invariants, toolchain safety, and cognitive best practices:

| Rule ID | Severity | Description |
|---|---|---|
| `ERR-FRAMEWORK-INCOMPLETE` | ERROR | Missing mandatory sections required by the selected framework (e.g., RISEN, CO-STAR, BAB, GoT, Meta-Prompting). |
| `ERR-TOOLCHAIN-MISMATCH` | ERROR | Prohibited tool references (e.g., `npm`/`yarn` referenced in a Python project, or `pytest`/`pip` in a TypeScript project). |
| `WARN-SANDWICH-STRUCTURE` | WARNING | Prompt length exceeds 150 words but lacks explicit Head/Tail anchors, risking Lost-in-the-Middle attention degradation. |
| `WARN-NAIVE-NEGATION` | WARNING | Excessive negative prohibitions (`do not`, `never`) without sufficient contrastive positive bounding (`must`, `ensure`). |
| `WARN-CLIENT-SECRET-LEAK` | WARNING | Server-only secrets (`DATABASE_URL`, private tokens) detected inside client-side components (`'use client'`). |
| `WARN-VAGUE-WORDS` | WARNING | Vague vocabulary (`thing`, `stuff`, `maybe`) that degrades output precision. |

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

# 3. Scaffold a grounded prompt template (e.g. RISEN or GoT)
uv run prompt-eng scaffold --repo example-repo --name auth-middleware --framework RISEN
uv run prompt-eng scaffold --repo example-repo --name dag-planner --framework got

# 4. Lint prompt against repository invariants and cognitive dynamics
uv run prompt-eng lint repos/example-repo/prompts/auth-middleware.md --repo example-repo

# 5. Score prompt quality across the 6-dimension rubric
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
uv run prompt-eng scaffold --repo <repo> --name <slug> [--framework <framework>] [--stdout]
```
Supported framework templates:
- **Procedural / Classic**: `RISEN` (default), `CO-STAR`, `BAB`, `ReAct`
- **Cognitive & Graph**: `got` (`Graph-of-Thoughts`), `meta-prompting`, `bot` (`Buffer-of-Thoughts`), `medprompt`
- **Web & Security**: `web-accessible` (WCAG 2.2 AA component), `defensive-action` (Next.js server action boundary)

### 4. `lint`
Validate prompt text or files against repository invariants, toolchain consistency, framework structure, cognitive dynamics, and boundary security.
```bash
uv run prompt-eng lint <path-or-text> --repo <repo> [--framework <framework>] [--strict]
```
- Validates framework completeness, sandwich structure, naive negation clusters, and client secret leakage.
- Returns exit code `0` on clean pass.
- Returns exit code `1` when errors are detected (or warnings when `--strict` is enabled).

### 5. `score`
Evaluate any raw or drafted prompt using the 6-dimension rubric (Clarity, Specificity, Context, Completeness, Structure, Attention & Cognitive Dynamics).
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
│       └── prompt-architect/     # Embedded local Antigravity skill (v4.0.0, 35 frameworks)
├── .claude/
│   └── skills/
│       └── prompt-architect/     # Embedded local Claude Code skill (v4.0.0, 35 frameworks)
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
│   │   ├── scaffolder.py         # Grounded prompt template generator (10 templates)
│   │   └── scorer.py             # 6-dimension heuristic rubric evaluator
│   └── transcripts/
│       ├── antigravity.py        # Antigravity session parser and XML sanitizer
│       ├── claude.py             # Claude Code transcript parser
│       └── resolver.py           # Multi-repo session locator
├── repos/
│   ├── .gitkeep
│   └── example-repo/
│       └── profile.yaml          # Public reference profile
└── tests/                        # Comprehensive unit and integration test suite (100+ tests)
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
