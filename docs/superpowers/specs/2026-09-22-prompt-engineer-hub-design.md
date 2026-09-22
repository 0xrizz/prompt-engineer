# Central Prompt Engineering Studio & Hub Architecture Design

**Date**: 2026-09-22  
**Status**: Approved  
**Scope**: Architectural  
**Target Repository**: `/home/rizz/dev/prompt-engineer`  

---

## 1. Executive Summary & Problem Statement

Developers working across multiple projects in `/home/rizz/dev/` face context switching and disparate prompting patterns when interacting with coding assistants and agent harnesses (`Antigravity`, `Antigravity CLI (agy)`, `Antigravity IDE`, and `Claude Code`). 

This project establishes `/home/rizz/dev/prompt-engineer` as a **Centralized Prompt Engineering Studio & Hub**. It enables the developer to:
1. Document and catalog the characteristics, tech stacks, rules, and constraints of every repository in `/home/rizz/dev/`.
2. Parse and summarize conversation transcripts from session logs across all four supported harnesses to extract critical problem context without flooding token limits.
3. Systematically engineer precision prompts tailored to the active session context using the **`prompt-architect`** framework (31 frameworks across 7 intent categories, 5-dimension rubric scoring, and template injection).
4. Maintain a fully isolated, project-scoped evolution of the `prompt-architect` skill using **Antigravity Skill Shadowing**, allowing local adaptations without altering or polluting global machine skills.
5. Persist structured prompts per repository and present clean, copy-pasteable prompt deliverables ready for immediate use in target sessions.

---

## 2. System Architecture

```
/home/rizz/dev/prompt-engineer/
├── .agents/
│   ├── skills.json                # Explicit workspace skill declarations & scoping
│   └── skills/
│       └── prompt-architect/      # Embedded & shadowed skill for Antigravity / agy
├── .claude/
│   └── skills/
│       └── prompt-architect/      # Embedded skill for Claude Code
├── AGENTS.md                      # Antigravity agent system instructions & skill invariants
├── CLAUDE.md                      # Claude Code system instructions & skill invariants
├── bin/
│   └── prompt-eng                 # Executable CLI wrapper (chmod +x)
├── prompt_eng/                    # Zero-dependency Python 3 package
│   ├── __init__.py
│   ├── cli.py                     # CLI entrypoint (scan, transcript, profile, list)
│   ├── scanner.py                 # Multi-repo scanner (/home/rizz/dev/*)
│   ├── models.py                  # Dataclasses: RepoProfile, SessionSummary, PromptSpec
│   └── transcripts/               # Transcript ingestion & extraction engine
│       ├── __init__.py
│       ├── antigravity.py         # JSONL parser for Antigravity / agy / IDE logs
│       ├── claude.py              # JSONL/session parser for Claude Code
│       └── resolver.py            # Automatic latest session finder & router
├── repos/                         # Per-repository knowledge & prompt studio
│   ├── 0x-arbiter/
│   │   ├── profile.yaml           # Metadata, stack, invariants, agent instructions
│   │   └── prompts/               # Stored prompts crafted for 0x-arbiter
│   ├── agy-os/
│   │   ├── profile.yaml
│   │   └── prompts/
│   └── ... (scanned for all repos in /home/rizz/dev/)
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-09-22-prompt-engineer-hub-design.md
```

---

## 3. Core Components

### 3.1 Repository Profiler & Scanner (`prompt_eng.scanner`)
- **Target Search Root**: `/home/rizz/dev/*` (skips `prompt-engineer` itself and temporary/archived scratch folders).
- **Detection Capabilities**:
  - Package manifests: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `requirements.txt`.
  - Harness instructions: `AGENTS.md`, `CLAUDE.md`, `.agents/rules/`, `.claude/rules/`.
  - Installed skills: `.agents/skills/`, `.claude/skills/`, `components/skills/`.
  - Git status & remotes.
- **Profile Output Format (`repos/<name>/profile.yaml`)**:
  ```yaml
  name: 0x-arbiter
  path: /home/rizz/dev/0x-arbiter
  description: Evaluation harness and benchmarking engine for custom Claude Code components
  stack:
    language: python
    package_manager: uv
    test_framework: pytest
    linter: ruff
  harness:
    instructions_files:
      - AGENTS.md
      - CLAUDE.md
    active_skills:
      - prompt-architect
  invariants:
    - Testing domain separation: Harness unit tests offline via pytest (<1s)
    - Zero-stall execution: Close stdin and non-interactive flags
  last_scanned: "2026-09-22T16:05:00"
  ```

### 3.2 Multi-Harness Transcript Resolver & Extractor (`prompt_eng.transcripts`)
Transcripts contain thousands of raw JSON lines (thinking blocks, tool inputs/outputs, base64 payloads). The extractor condenses these into an actionable context snapshot.

- **Supported Harnesses**:
  1. **Antigravity / `agy` / Antigravity IDE**:
     - Path pattern: `~/.gemini/antigravity/brain/<conv-id>/.system_generated/logs/transcript.jsonl`
     - Metadata source: `~/.gemini/antigravity/conversations/` or conversation directory.
  2. **Claude Code**:
     - Path pattern: `~/.claude/projects/<project-slug>/` or local `.claude/` session logs.
- **Resolver Engine (`resolver.py`)**:
  - Automatically identifies the newest session matching a given repository target by comparing timestamps and workspace directory tags.
  - Supports explicit targeting via `--session <id_or_path>` or `--file <path>`.
- **Extraction Logic**:
  - Extracts **Initial User Goal**: The first `USER_INPUT` or prompt initiating the task.
  - Extracts **Key Tool Actions**: Significant commands run, files edited, errors reported.
  - Identifies **Blockers / Failures**: Terminal errors, test failures, or syntax/lint issues.
  - Extracts **Latest Conversation State**: The last model response or unresolved question.
  - Produces clean Markdown or structured JSON ready for the `prompt-architect` skill.

### 3.3 CLI Interface (`bin/prompt-eng` & `prompt_eng.cli`)
A zero-dependency Python 3 CLI tool.

- `prompt-eng scan`:
  Scans `/home/rizz/dev/*` and creates/updates `repos/<name>/profile.yaml` for each repo.
- `prompt-eng transcript --repo <name> [--latest] [--session <id>] [--format md|json]`:
  Locates and extracts a concise summary of the conversation session.
- `prompt-eng profile <name>`:
  Displays the documented profile, instructions, and existing prompts for a repository.
- `prompt-eng list`:
  Lists all tracked repositories, their detected tech stacks, and count of engineered prompts.
- `prompt-eng save-prompt --repo <name> --name <slug> --framework <fw> --content-file <file>`:
  Helper to persist an engineered prompt into `repos/<name>/prompts/<slug>.md`.

### 3.4 Embedded Skill Integration & Workspace Shadowing (`prompt-architect`)

#### A. Antigravity Loading Priority & Precedence
Antigravity evaluates customizations using a strict hierarchical order:
1. **Workspace Project** (`.agents/skills/<name>/SKILL.md` in repository root) — **Highest Priority**
2. **Declared Configurations** (`.agents/skills.json`)
3. **Global Discovery** (`~/.gemini/config/skills/`)
4. **Built-in Customizations**

#### B. Skill Shadowing Behavior
- When `.agents/skills/prompt-architect/SKILL.md` is present in `prompt-engineer`, Antigravity **automatically shadows (overrides)** the global version in `~/.gemini/config/skills/prompt-architect/` for all agent interactions inside this repository.
- **Global Skill Immutability**: The global skill in `~/.gemini/config/skills/` remains completely unmodified and continues to serve other repositories on the machine.
- **Local Evolution**: Any custom adaptations (e.g. specialized templates, repo-aware prompts, tailored rubric weights) are made exclusively to `.agents/skills/prompt-architect/` within this repository.

#### C. Declarative Configuration & Agent Invariants
- An explicit `.agents/skills.json` will be placed in the workspace:
  ```json
  {
    "entries": [
      {
        "path": ".agents/skills"
      }
    ]
  }
  ```
- `AGENTS.md` and `CLAUDE.md` explicitly instruct the AI:
  > "Always resolve `prompt-architect` using the local workspace definition at `.agents/skills/prompt-architect/SKILL.md`. Never defer to or import the global machine skill."

### 3.5 Generated Prompt Lifecycle & Storage
Prompts are saved in `repos/<repo-name>/prompts/<slug>.md` with YAML frontmatter:
```markdown
---
name: web-dev-eval-prompt
repo: 0x-arbiter
framework: RISEN
target_harness: claude-code
session_id: 59babdf8-68bf-478e-8aed-b508ef1dbb63
score:
  clarity: 9
  specificity: 8
  context: 9
  completeness: 8
  structure: 9
  overall: 8.6
created_at: 2026-09-22
---

[Clean prompt content ready for verbatim copy-paste into target session]
```
The agent and CLI always present the final prompt as a flat, clean markdown code block at the conclusion of the interaction so the user can easily copy and paste it into the target session without modifying target repo files.

---

## 4. Operational Invariants

1. **Target Repo Isolation**: Never directly alter, write files, or mutate source code in `/home/rizz/dev/<other-repo>/`. All profiles, notes, transcripts summaries, and engineered prompts stay strictly contained inside `prompt-engineer/`.
2. **Skill Isolation & Shadowing**: The workspace skill `.agents/skills/prompt-architect/` must strictly override the global skill for this workspace. The global skill in `~/.gemini/config/skills/` must never be edited, deleted, or polluted.
3. **Token Efficiency**: Never dump raw full-length JSONL transcripts into conversational context. Always pass through `prompt_eng.transcripts` extraction.
4. **Zero External Runtime Dependencies**: The core Python package `prompt_eng` must run on Python 3 standard libraries without requiring `pip install` or external package installation.

---

## 5. Verification Plan

1. **CLI Unit & Functional Tests**:
   - `python3 -m unittest discover -s tests` to verify scanner, models, and transcript parsers.
2. **Scanner Verification**:
   - Run `bin/prompt-eng scan` and verify that all repositories in `/home/rizz/dev/` (`0x-arbiter`, `agy-os`, `audio-composer`, etc.) generate valid `repos/<name>/profile.yaml` files.
3. **Transcript Parser Verification**:
   - Run `bin/prompt-eng transcript --session <current-conversation-id>` on current Antigravity transcript and verify that a concise, accurate markdown summary is produced.
4. **Skill Isolation Verification**:
   - Verify that `.agents/skills/prompt-architect/SKILL.md` exists locally.
   - Verify that `.agents/skills.json` defines the local workspace path.
   - Confirm that global `~/.gemini/config/skills/prompt-architect/` is unaffected and remains identical.
