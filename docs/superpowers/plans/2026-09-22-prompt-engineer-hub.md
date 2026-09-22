# Central Prompt Engineering Studio & Hub Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a centralized Prompt Engineering Studio and multi-repo hub in `/home/rizz/dev/prompt-engineer` capable of cataloging target repository characteristics across `/home/rizz/dev/*`, parsing multi-harness conversation transcripts (Antigravity and Claude Code), scoring prompts across 5 dimensions, and executing local workspace-shadowed `prompt-architect` workflows.

**Architecture:** A zero-dependency Python 3 core package (`prompt_eng`) providing a multi-repo scanner, multi-harness session transcript extractor, rubric scorer, visual diff engine, and unified CLI wrapper (`bin/prompt-eng`). Complemented by locally shadowed `prompt-architect` skills in `.agents/skills/` and `.claude/skills/` with strict workspace scoping and comprehensive SOP instructions in `AGENTS.md` and `CLAUDE.md`.

**Tech Stack:** Python 3 (standard library: `argparse`, `pathlib`, `json`, `re`, `dataclasses`, `difflib`, `subprocess`), `pytest` / `unittest` (dual-compatible offline test suite), `ruff` (dev linter/formatter).

**Spec:** [`docs/superpowers/specs/2026-09-22-prompt-engineer-hub-design.md`](file:///home/rizz/dev/prompt-engineer/docs/superpowers/specs/2026-09-22-prompt-engineer-hub-design.md)

## Global Constraints

- **Target Repo Isolation:** Never directly alter, write files, or mutate source code in any target repository under `/home/rizz/dev/*`. All generated profiles, summaries, and prompts must remain within `/home/rizz/dev/prompt-engineer/`.
- **Zero External Runtime Dependencies:** The runtime package `prompt_eng` must run strictly on Python 3 standard library modules without requiring `pip install`.
- **Dual-Mode Offline Tests:** All test files must be runnable via both `pytest tests/` and `python3 -m unittest discover -s tests` with zero network egress and execution time <2 seconds.
- **Skill Shadowing Invariant:** Workspace skill `.agents/skills/prompt-architect/` must strictly override the global machine skill for this repository without altering or deleting `~/.gemini/config/skills/prompt-architect/`.
- **Strict TDD Granularity:** Every implementation task must follow the strict red-green-commit cycle (Write failing test $\rightarrow$ Verify failure $\rightarrow$ Minimal implementation $\rightarrow$ Verify pass $\rightarrow$ Commit).

---

### Task 1: Scaffolding, Packaging & Environment Setup

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `.editorconfig`
- Create: `bin/prompt-eng`
- Create: `prompt_eng/__init__.py`
- Create: `tests/__init__.py`
- Test: `tests/test_scaffolding.py`

**Interfaces:**
- Consumes: None (Root bootstrapping)
- Produces: Executable `bin/prompt-eng` runnable via `python3` that prints version/usage, and importable `prompt_eng` package.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_scaffolding.py
import subprocess
import sys
import unittest
from pathlib import Path

class TestScaffolding(unittest.TestCase):
    def test_package_import(self):
        import prompt_eng
        self.assertTrue(hasattr(prompt_eng, "__version__"))
        self.assertEqual(prompt_eng.__version__, "0.1.0")

    def test_bin_executable_runs(self):
        root = Path(__file__).resolve().parent.parent
        bin_path = root / "bin" / "prompt-eng"
        self.assertTrue(bin_path.exists(), "bin/prompt-eng does not exist")
        res = subprocess.run([sys.executable, str(bin_path), "--version"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("prompt-eng 0.1.0", res.stdout.strip())

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_scaffolding.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'prompt_eng'`

- [ ] **Step 3: Write minimal implementation**

Create `pyproject.toml`:
```toml
[project]
name = "prompt-engineer"
version = "0.1.0"
description = "Centralized Prompt Engineering Studio & Multi-Repo Hub"
readme = "README.md"
requires-python = ">=3.10"
dependencies = []

[project.scripts]
prompt-eng = "prompt_eng.cli:main"

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "ruff>=0.5.0",
]

[tool.ruff]
line-length = 100
target-version = "py310"
```

Create `.gitignore`:
```gitignore
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.env
.venv
env/
venv/
ENV/
.pytest_cache/
.ruff_cache/
.coverage
htmlcov/
.DS_Store
```

Create `.editorconfig`:
```ini
root = true

[*]
indent_style = space
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.{json,yaml,yml,md}]
indent_size = 2
```

Create `prompt_eng/__init__.py`:
```python
"""Centralized Prompt Engineering Studio & Multi-Repo Hub."""
__version__ = "0.1.0"
```

Create `tests/__init__.py`:
```python
# Empty test package marker
```

Create `bin/prompt-eng` (and run `chmod +x bin/prompt-eng`):
```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--version":
        import prompt_eng
        print(f"prompt-eng {prompt_eng.__version__}")
        sys.exit(0)
    # Forward to prompt_eng.cli when available
    try:
        from prompt_eng.cli import main
        sys.exit(main())
    except ImportError:
        print(f"prompt-eng 0.1.0 (CLI bootstrapping)")
        sys.exit(0)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `chmod +x bin/prompt-eng && python3 -m unittest tests/test_scaffolding.py -v`  
Expected: PASS with 2 tests ok.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml .gitignore .editorconfig bin/prompt-eng prompt_eng/__init__.py tests/__init__.py tests/test_scaffolding.py
git commit -m "chore: bootstrap project scaffolding, packaging, and bin runner"
```

---

### Task 2: Core Domain Models & Serialization

**Files:**
- Create: `prompt_eng/models.py`
- Test: `tests/test_models.py`

**Interfaces:**
- Consumes: Standard library `dataclasses`, `json`, `typing`
- Produces:
  - `RepoProfile(name, path, description, stack, harness, invariants, last_scanned)`
  - `StackInfo(language, package_manager, test_framework, linter)`
  - `HarnessInfo(instruction_files, active_skills)`
  - `SessionSummary(harness, session_id, repo_name, user_goal, key_tools, errors, last_turn_state)`
  - `RubricScore(clarity, specificity, context, completeness, structure, overall)`
  - `PromptSpec(name, repo, framework, target_harness, session_id, score, content, created_at)`
  - Helpers: `dump_yaml_simple(data: dict) -> str`, `load_yaml_simple(text: str) -> dict`, `parse_frontmatter_markdown(text: str) -> tuple[dict, str]`, `dump_frontmatter_markdown(meta: dict, body: str) -> str`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_models.py
import unittest
from prompt_eng.models import (
    RepoProfile,
    StackInfo,
    HarnessInfo,
    RubricScore,
    PromptSpec,
    dump_yaml_simple,
    load_yaml_simple,
    parse_frontmatter_markdown,
    dump_frontmatter_markdown,
)

class TestModels(unittest.TestCase):
    def test_rubric_score_calculation(self):
        score = RubricScore(clarity=8, specificity=7, context=9, completeness=8, structure=8)
        self.assertAlmostEqual(score.overall, 8.0, places=1)

    def test_yaml_roundtrip_simple(self):
        data = {
            "name": "0x-arbiter",
            "path": "/home/rizz/dev/0x-arbiter",
            "stack": {
                "language": "python",
                "package_manager": "uv"
            },
            "invariants": ["Zero-stall execution", "Testing domain separation"]
        }
        yaml_str = dump_yaml_simple(data)
        self.assertIn("name: 0x-arbiter", yaml_str)
        self.assertIn("  language: python", yaml_str)
        self.assertIn("- Zero-stall execution", yaml_str)
        parsed = load_yaml_simple(yaml_str)
        self.assertEqual(parsed["name"], "0x-arbiter")
        self.assertEqual(parsed["stack"]["language"], "python")
        self.assertEqual(len(parsed["invariants"]), 2)

    def test_frontmatter_markdown_roundtrip(self):
        meta = {"name": "test-prompt", "framework": "RISEN", "score": {"overall": 8.5}}
        body = "This is the clean prompt content."
        serialized = dump_frontmatter_markdown(meta, body)
        self.assertTrue(serialized.startswith("---\n"))
        self.assertIn("framework: RISEN", serialized)
        self.assertTrue(serialized.endswith("This is the clean prompt content.\n"))

        parsed_meta, parsed_body = parse_frontmatter_markdown(serialized)
        self.assertEqual(parsed_meta["framework"], "RISEN")
        self.assertEqual(parsed_body.strip(), "This is the clean prompt content.")

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_models.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'prompt_eng.models'`

- [ ] **Step 3: Write minimal implementation**

Create `prompt_eng/models.py`:
```python
"""Domain models and serialization utilities for prompt-engineer."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple
import re

@dataclass
class StackInfo:
    language: str = "unknown"
    package_manager: str = "unknown"
    test_framework: str = "unknown"
    linter: str = "unknown"

@dataclass
class HarnessInfo:
    instruction_files: List[str] = field(default_factory=list)
    active_skills: List[str] = field(default_factory=list)

@dataclass
class RepoProfile:
    name: str
    path: str
    description: str = ""
    stack: StackInfo = field(default_factory=StackInfo)
    harness: HarnessInfo = field(default_factory=HarnessInfo)
    invariants: List[str] = field(default_factory=list)
    last_scanned: str = ""

@dataclass
class SessionSummary:
    harness: str  # 'antigravity', 'claude-code'
    session_id: str
    repo_name: str
    user_goal: str
    key_tools: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    last_turn_state: str = ""

@dataclass
class RubricScore:
    clarity: float
    specificity: float
    context: float
    completeness: float
    structure: float
    overall: float = field(init=False)

    def __post_init__(self):
        self.overall = round(
            (self.clarity + self.specificity + self.context + self.completeness + self.structure) / 5.0,
            1,
        )

@dataclass
class PromptSpec:
    name: str
    repo: str
    framework: str
    target_harness: str
    session_id: str
    score: RubricScore
    content: str
    created_at: str

def dump_yaml_simple(data: Dict[str, Any], indent: int = 0) -> str:
    """Lightweight zero-dependency YAML serializer for nested dictionaries and lists."""
    lines = []
    prefix = " " * indent
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(dump_yaml_simple(value, indent + 2))
        elif isinstance(value, list):
            lines.append(f"{prefix}{key}:")
            for item in value:
                if isinstance(item, dict):
                    nested = dump_yaml_simple(item, indent + 4)
                    lines.append(f"{prefix}  - " + nested.lstrip())
                else:
                    lines.append(f"{prefix}  - {item}")
        else:
            val_str = "null" if value is None else str(value)
            lines.append(f"{prefix}{key}: {val_str}")
    return "\n".join(lines)

def load_yaml_simple(yaml_str: str) -> Dict[str, Any]:
    """Lightweight zero-dependency YAML parser for nested dictionaries and lists."""
    result: Dict[str, Any] = {}
    lines = yaml_str.splitlines()
    stack: List[Tuple[int, Any]] = [(-1, result)]
    
    for line in lines:
        if not line.strip() or line.strip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        
        while len(stack) > 1 and stack[-1][0] >= indent:
            stack.pop()
            
        current = stack[-1][1]
        
        if stripped.startswith("- "):
            val = stripped[2:].strip()
            # Handle key-value inside list item
            if ":" in val:
                k, v = val.split(":", 1)
                item = {k.strip(): v.strip()}
                if isinstance(current, list):
                    current.append(item)
                    stack.append((indent + 2, item))
            else:
                if isinstance(current, list):
                    current.append(val)
        elif ":" in stripped:
            key, val = stripped.split(":", 1)
            key = key.strip()
            val = val.strip()
            if not val:
                # Next is nested dict or list
                # Lookahead to see if list
                new_container: Any = {}
                if isinstance(current, dict):
                    current[key] = new_container
                stack.append((indent, new_container))
            else:
                if isinstance(current, dict):
                    current[key] = val
                elif isinstance(current, list) and current and isinstance(current[-1], dict):
                    current[-1][key] = val
                    
    # Convert dummy dict containers that only had list appends
    def _fix_containers(d):
        if isinstance(d, dict):
            for k, v in list(d.items()):
                if isinstance(v, dict) and not v:
                    d[k] = []
                else:
                    _fix_containers(v)
    _fix_containers(result)
    return result

def dump_frontmatter_markdown(meta: Dict[str, Any], body: str) -> str:
    yaml_part = dump_yaml_simple(meta)
    return f"---\n{yaml_part}\n---\n\n{body.strip()}\n"

def parse_frontmatter_markdown(text: str) -> Tuple[Dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta_str = parts[1].strip()
    body_str = parts[2].strip()
    meta = load_yaml_simple(meta_str)
    return meta, body_str
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_models.py -v`  
Expected: PASS with 3 tests ok.

- [ ] **Step 5: Commit**

```bash
git add prompt_eng/models.py tests/test_models.py
git commit -m "feat: add domain models and lightweight yaml/frontmatter serialization"
```

---

### Task 3: Multi-Harness Transcript Extraction Engine

**Files:**
- Create: `prompt_eng/transcripts/__init__.py`
- Create: `prompt_eng/transcripts/antigravity.py`
- Create: `prompt_eng/transcripts/claude.py`
- Create: `prompt_eng/transcripts/resolver.py`
- Create: `tests/fixtures/antigravity_sample.jsonl`
- Create: `tests/fixtures/claude_sample.jsonl`
- Test: `tests/test_transcripts.py`

**Interfaces:**
- Consumes: `prompt_eng.models.SessionSummary`
- Produces:
  - `parse_antigravity_transcript(jsonl_path: Path, repo_name: str) -> SessionSummary`
  - `parse_claude_transcript(jsonl_path: Path, repo_name: str) -> SessionSummary`
  - `SessionResolver.find_latest_session(repo_name: str, target_dir: Optional[Path]) -> Tuple[str, Path]`
  - `render_session_summary_markdown(summary: SessionSummary) -> str`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_transcripts.py
import json
import unittest
from pathlib import Path
from prompt_eng.transcripts.antigravity import parse_antigravity_transcript
from prompt_eng.transcripts.claude import parse_claude_transcript
from prompt_eng.transcripts.resolver import render_session_summary_markdown

class TestTranscripts(unittest.TestCase):
    def setUp(self):
        self.fixtures_dir = Path(__file__).resolve().parent / "fixtures"
        self.fixtures_dir.mkdir(parents=True, exist_ok=True)

        self.ag_path = self.fixtures_dir / "antigravity_sample.jsonl"
        with open(self.ag_path, "w", encoding="utf-8") as f:
            f.write(json.dumps({
                "type": "USER_INPUT",
                "content": "Fix the failing test in tests/unit/test_catalog.py"
            }) + "\n")
            f.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "tool_calls": [{"toolAction": "Running command", "toolSummary": "Run pytest"}]
            }) + "\n")
            f.write(json.dumps({
                "type": "TOOL_RESPONSE",
                "content": "FAILED tests/unit/test_catalog.py - AssertionError: 3 != 4"
            }) + "\n")
            f.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "content": "The catalog count expectation is mismatched. Should we update the catalog?"
            }) + "\n")

        self.cl_path = self.fixtures_dir / "claude_sample.jsonl"
        with open(self.cl_path, "w", encoding="utf-8") as f:
            f.write(json.dumps({
                "role": "user",
                "content": "Refactor auth middleware to use bearer token"
            }) + "\n")
            f.write(json.dumps({
                "role": "assistant",
                "content": "I inspected middleware.ts and encountered a circular import error."
            }) + "\n")

    def test_parse_antigravity(self):
        summary = parse_antigravity_transcript(self.ag_path, repo_name="0x-arbiter")
        self.assertEqual(summary.harness, "antigravity")
        self.assertIn("Fix the failing test", summary.user_goal)
        self.assertEqual(len(summary.key_tools), 1)
        self.assertIn("AssertionError", summary.errors[0])
        self.assertIn("Should we update the catalog?", summary.last_turn_state)

    def test_parse_claude(self):
        summary = parse_claude_transcript(self.cl_path, repo_name="agy-os")
        self.assertEqual(summary.harness, "claude-code")
        self.assertIn("Refactor auth middleware", summary.user_goal)
        self.assertIn("circular import error", summary.last_turn_state)

    def test_render_summary_markdown(self):
        summary = parse_antigravity_transcript(self.ag_path, repo_name="0x-arbiter")
        md = render_session_summary_markdown(summary)
        self.assertIn("## Session Context Summary", md)
        self.assertIn("**Harness**: antigravity", md)
        self.assertIn("Fix the failing test", md)

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_transcripts.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'prompt_eng.transcripts'`

- [ ] **Step 3: Write minimal implementation**

Create `prompt_eng/transcripts/__init__.py`:
```python
"""Transcript ingestion and parsing for Antigravity and Claude Code."""
from .antigravity import parse_antigravity_transcript
from .claude import parse_claude_transcript
from .resolver import SessionResolver, render_session_summary_markdown

__all__ = [
    "parse_antigravity_transcript",
    "parse_claude_transcript",
    "SessionResolver",
    "render_session_summary_markdown",
]
```

Create `prompt_eng/transcripts/antigravity.py`:
```python
"""Parser for Antigravity / agy / Antigravity IDE JSONL transcript logs."""
import json
from pathlib import Path
from prompt_eng.models import SessionSummary

def parse_antigravity_transcript(jsonl_path: Path, repo_name: str = "") -> SessionSummary:
    user_goal = ""
    tools = []
    errors = []
    last_turn_state = ""
    session_id = jsonl_path.stem

    if not jsonl_path.exists():
        raise FileNotFoundError(f"Transcript file not found: {jsonl_path}")

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            entry_type = entry.get("type", "")
            content = entry.get("content", "")

            if entry_type == "USER_INPUT" and not user_goal:
                user_goal = str(content).strip()

            if "tool_calls" in entry and isinstance(entry["tool_calls"], list):
                for tc in entry["tool_calls"]:
                    action = tc.get("toolAction", tc.get("toolSummary", "tool_call"))
                    tools.append(action)

            if entry_type == "TOOL_RESPONSE" and any(w in str(content).lower() for w in ["fail", "error", "traceback"]):
                snippet = str(content).strip().split("\n")[0][:120]
                errors.append(snippet)

            if entry_type == "PLANNER_RESPONSE" and content:
                last_turn_state = str(content).strip()[:300]

    return SessionSummary(
        harness="antigravity",
        session_id=session_id,
        repo_name=repo_name,
        user_goal=user_goal or "No explicit user goal recorded",
        key_tools=tools[-10:],
        errors=errors[-5:],
        last_turn_state=last_turn_state,
    )
```

Create `prompt_eng/transcripts/claude.py`:
```python
"""Parser for Claude Code JSONL/session transcripts."""
import json
from pathlib import Path
from prompt_eng.models import SessionSummary

def parse_claude_transcript(jsonl_path: Path, repo_name: str = "") -> SessionSummary:
    user_goal = ""
    tools = []
    errors = []
    last_turn_state = ""
    session_id = jsonl_path.stem

    if not jsonl_path.exists():
        raise FileNotFoundError(f"Claude transcript not found: {jsonl_path}")

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            role = entry.get("role", "")
            content = entry.get("content", "")

            if role == "user" and not user_goal:
                user_goal = str(content).strip()

            if "tool_use" in str(entry) or "command" in str(entry):
                tools.append("claude_tool_invocation")

            if any(w in str(content).lower() for w in ["error", "fatal", "failed"]):
                errors.append(str(content).strip().split("\n")[0][:120])

            if role == "assistant" and content:
                last_turn_state = str(content).strip()[:300]

    return SessionSummary(
        harness="claude-code",
        session_id=session_id,
        repo_name=repo_name,
        user_goal=user_goal or "No explicit user goal recorded",
        key_tools=tools[-10:],
        errors=errors[-5:],
        last_turn_state=last_turn_state,
    )
```

Create `prompt_eng/transcripts/resolver.py`:
```python
"""Session resolver to find and format latest session transcripts."""
from pathlib import Path
from typing import Optional, Tuple
from prompt_eng.models import SessionSummary
from .antigravity import parse_antigravity_transcript
from .claude import parse_claude_transcript

class SessionResolver:
    @staticmethod
    def resolve_session(
        repo_name: str,
        session_id: Optional[str] = None,
        file_path: Optional[Path] = None,
    ) -> SessionSummary:
        if file_path and file_path.exists():
            if "claude" in str(file_path).lower():
                return parse_claude_transcript(file_path, repo_name=repo_name)
            return parse_antigravity_transcript(file_path, repo_name=repo_name)

        # Default paths to check
        home = Path.home()
        ag_brain = home / ".gemini" / "antigravity" / "brain"
        claude_projects = home / ".claude" / "projects"

        # Check explicit session_id in Antigravity brain
        if session_id:
            candidate = ag_brain / session_id / ".system_generated" / "logs" / "transcript.jsonl"
            if candidate.exists():
                return parse_antigravity_transcript(candidate, repo_name=repo_name)

        # Look for most recent session in ag_brain
        if ag_brain.exists():
            sessions = sorted(ag_brain.glob("*/.system_generated/logs/transcript.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
            if sessions:
                return parse_antigravity_transcript(sessions[0], repo_name=repo_name)

        raise FileNotFoundError(f"No active session transcript found for repo: {repo_name}")

def render_session_summary_markdown(summary: SessionSummary) -> str:
    tools_list = "\n".join(f"- `{t}`" for t in summary.key_tools) if summary.key_tools else "None recorded."
    errors_list = "\n".join(f"- `{e}`" for e in summary.errors) if summary.errors else "No errors detected."
    return f"""## Session Context Summary
- **Target Repository**: {summary.repo_name}
- **Harness**: {summary.harness}
- **Session ID**: `{summary.session_id}`

### 🎯 Initial User Goal
{summary.user_goal}

### 🛠️ Key Tools & Commands Executed
{tools_list}

### ⚠️ Blockers & Errors
{errors_list}

### 💬 Latest Conversation Turn
{summary.last_turn_state}
"""
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_transcripts.py -v`  
Expected: PASS with 3 tests ok.

- [ ] **Step 5: Commit**

```bash
git add prompt_eng/transcripts/ tests/test_transcripts.py
git commit -m "feat: implement multi-harness transcript parsers and session resolver"
```

---

### Task 4: Multi-Repository Scanner & Profiler

**Files:**
- Create: `prompt_eng/scanner.py`
- Test: `tests/test_scanner.py`

**Interfaces:**
- Consumes: `prompt_eng.models.RepoProfile`, `StackInfo`, `HarnessInfo`, `dump_yaml_simple`
- Produces:
  - `scan_repository(repo_path: Path) -> RepoProfile`
  - `scan_all_repositories(dev_root: Path, output_repos_dir: Path) -> List[RepoProfile]`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_scanner.py
import json
import tempfile
import unittest
from pathlib import Path
from prompt_eng.scanner import scan_repository, scan_all_repositories

class TestScanner(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp_dir.name)

        # Mock repo 1: Python project
        self.repo1 = self.root / "py-service"
        self.repo1.mkdir()
        (self.repo1 / "pyproject.toml").write_text('[project]\nname="py-service"\n', encoding="utf-8")
        (self.repo1 / "AGENTS.md").write_text("# Py Service Invariants\n- Fast tests\n", encoding="utf-8")

        # Mock repo 2: Node project
        self.repo2 = self.root / "web-app"
        self.repo2.mkdir()
        (self.repo2 / "package.json").write_text('{"name": "web-app", "scripts": {"test": "jest"}}\n', encoding="utf-8")
        (self.repo2 / "CLAUDE.md").write_text("# Claude Guidelines\n", encoding="utf-8")

        self.output_dir = self.root / "repos"

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_scan_single_repo(self):
        profile = scan_repository(self.repo1)
        self.assertEqual(profile.name, "py-service")
        self.assertEqual(profile.stack.language, "python")
        self.assertIn("AGENTS.md", profile.harness.instruction_files)
        self.assertIn("Fast tests", profile.invariants[0])

    def test_scan_all_repositories(self):
        profiles = scan_all_repositories(self.root, self.output_dir)
        self.assertEqual(len(profiles), 2)
        p1_file = self.output_dir / "py-service" / "profile.yaml"
        p2_file = self.output_dir / "web-app" / "profile.yaml"
        self.assertTrue(p1_file.exists())
        self.assertTrue(p2_file.exists())

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_scanner.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'prompt_eng.scanner'`

- [ ] **Step 3: Write minimal implementation**

Create `prompt_eng/scanner.py`:
```python
"""Multi-repository scanner to detect stack, harness instructions, and invariants."""
from datetime import datetime
from pathlib import Path
from typing import List
from prompt_eng.models import RepoProfile, StackInfo, HarnessInfo, dump_yaml_simple

def scan_repository(repo_path: Path) -> RepoProfile:
    name = repo_path.name
    stack = StackInfo()
    harness = HarnessInfo()
    invariants: List[str] = []

    # Detect package & build manifests
    if (repo_path / "pyproject.toml").exists():
        stack.language = "python"
        content = (repo_path / "pyproject.toml").read_text(encoding="utf-8", errors="ignore")
        stack.package_manager = "uv" if "uv" in content else "pip/poetry"
        stack.test_framework = "pytest" if "pytest" in content else "unittest"
        stack.linter = "ruff" if "ruff" in content else "flake8"
    elif (repo_path / "package.json").exists():
        stack.language = "javascript/typescript"
        content = (repo_path / "package.json").read_text(encoding="utf-8", errors="ignore")
        stack.package_manager = "pnpm" if (repo_path / "pnpm-lock.yaml").exists() else "npm"
        stack.test_framework = "jest" if "jest" in content else "vitest" if "vitest" in content else "npm test"
        stack.linter = "eslint" if "eslint" in content else "prettier"
    elif (repo_path / "Cargo.toml").exists():
        stack.language = "rust"
        stack.package_manager = "cargo"
        stack.test_framework = "cargo test"
        stack.linter = "clippy"
    elif (repo_path / "go.mod").exists():
        stack.language = "go"
        stack.package_manager = "go modules"
        stack.test_framework = "go test"
        stack.linter = "golangci-lint"

    # Detect harness files
    for doc in ["AGENTS.md", "CLAUDE.md", "GEMINI.md"]:
        if (repo_path / doc).exists():
            harness.instruction_files.append(doc)
            text = (repo_path / doc).read_text(encoding="utf-8", errors="ignore")
            for line in text.splitlines():
                if line.strip().startswith("- ") and any(k in line.lower() for k in ["test", "rule", "invariant", "require", "never"]):
                    invariants.append(line.strip()[2:])

    # Detect skills
    for skill_dir in [repo_path / ".agents" / "skills", repo_path / ".claude" / "skills", repo_path / "components" / "skills"]:
        if skill_dir.exists() and skill_dir.is_dir():
            for child in skill_dir.iterdir():
                if child.is_dir() and (child / "SKILL.md").exists():
                    if child.name not in harness.active_skills:
                        harness.active_skills.append(child.name)

    return RepoProfile(
        name=name,
        path=str(repo_path.resolve()),
        description=f"Auto-profiled {stack.language} workspace",
        stack=stack,
        harness=harness,
        invariants=invariants[:10],
        last_scanned=datetime.now().isoformat(),
    )

def scan_all_repositories(dev_root: Path, output_repos_dir: Path) -> List[RepoProfile]:
    profiles = []
    output_repos_dir.mkdir(parents=True, exist_ok=True)

    for item in dev_root.iterdir():
        if not item.is_dir() or item.name.startswith(".") or item.name in ["prompt-engineer", "repos"]:
            continue
        # Skip temporary folders
        if "delete this" in item.name.lower():
            continue

        profile = scan_repository(item)
        profiles.append(profile)

        # Write to repos/<name>/profile.yaml
        repo_studio_dir = output_repos_dir / profile.name
        repo_studio_dir.mkdir(parents=True, exist_ok=True)
        (repo_studio_dir / "prompts").mkdir(exist_ok=True)

        meta = {
            "name": profile.name,
            "path": profile.path,
            "description": profile.description,
            "stack": {
                "language": profile.stack.language,
                "package_manager": profile.stack.package_manager,
                "test_framework": profile.stack.test_framework,
                "linter": profile.stack.linter,
            },
            "harness": {
                "instruction_files": profile.harness.instruction_files,
                "active_skills": profile.harness.active_skills,
            },
            "invariants": profile.invariants,
            "last_scanned": profile.last_scanned,
        }
        (repo_studio_dir / "profile.yaml").write_text(dump_yaml_simple(meta) + "\n", encoding="utf-8")

    return profiles
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_scanner.py -v`  
Expected: PASS with 2 tests ok.

- [ ] **Step 5: Commit**

```bash
git add prompt_eng/scanner.py tests/test_scanner.py
git commit -m "feat: implement multi-repo scanner and profile generator"
```

---

### Task 5: Studio Suite Utilities (Scorer, Diff & Catalog)

**Files:**
- Create: `prompt_eng/studio/__init__.py`
- Create: `prompt_eng/studio/scorer.py`
- Create: `prompt_eng/studio/diff.py`
- Create: `prompt_eng/studio/catalog.py`
- Test: `tests/test_studio.py`

**Interfaces:**
- Consumes: `prompt_eng.models.RubricScore`, `parse_frontmatter_markdown`
- Produces:
  - `evaluate_rubric(prompt_text: str) -> RubricScore`
  - `render_rubric_table(score: RubricScore) -> str`
  - `compare_prompt_diff(before: str, after: str) -> str`
  - `query_prompt_catalog(repos_dir: Path, query: str) -> List[Dict[str, Any]]`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_studio.py
import tempfile
import unittest
from pathlib import Path
from prompt_eng.studio.scorer import evaluate_rubric, render_rubric_table
from prompt_eng.studio.diff import compare_prompt_diff
from prompt_eng.studio.catalog import query_prompt_catalog
from prompt_eng.models import dump_frontmatter_markdown

class TestStudio(unittest.TestCase):
    def test_rubric_evaluator(self):
        vague_prompt = "do the thing"
        score = evaluate_rubric(vague_prompt)
        self.assertLessEqual(score.overall, 5.0)

        structured_prompt = """
        Role: Expert Python Engineer
        Task: Refactor auth handler
        Context: Using fastapi 0.110 in 0x-arbiter
        Format: Return only python code block with unit test
        Constraints: Do not modify existing db schemas
        """
        good_score = evaluate_rubric(structured_prompt)
        self.assertGreaterEqual(good_score.overall, 7.0)
        table = render_rubric_table(good_score)
        self.assertIn("Clarity", table)
        self.assertIn("Overall", table)

    def test_diff_engine(self):
        before = "Write tests"
        after = "Write tests for auth handler using pytest"
        diff_output = compare_prompt_diff(before, after)
        self.assertIn("Write tests", diff_output)
        self.assertIn("auth handler", diff_output)

    def test_catalog_query(self):
        with tempfile.TemporaryDirectory() as tmp:
            repos_dir = Path(tmp)
            p_dir = repos_dir / "0x-arbiter" / "prompts"
            p_dir.mkdir(parents=True)
            content = dump_frontmatter_markdown({"framework": "RISEN", "target": "eval"}, "Write benchmark")
            (p_dir / "eval-benchmark.md").write_text(content, encoding="utf-8")

            results = query_prompt_catalog(repos_dir, "benchmark")
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["repo"], "0x-arbiter")

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_studio.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'prompt_eng.studio'`

- [ ] **Step 3: Write minimal implementation**

Create `prompt_eng/studio/__init__.py`:
```python
"""Studio suite tools: scoring, diffing, and catalog searching."""
from .scorer import evaluate_rubric, render_rubric_table
from .diff import compare_prompt_diff
from .catalog import query_prompt_catalog

__all__ = ["evaluate_rubric", "render_rubric_table", "compare_prompt_diff", "query_prompt_catalog"]
```

Create `prompt_eng/studio/scorer.py`:
```python
"""5-dimension rubric scoring engine based on prompt-architect guidelines."""
import re
from prompt_eng.models import RubricScore

def evaluate_rubric(prompt_text: str) -> RubricScore:
    text = prompt_text.strip()
    words = len(text.split())

    # Clarity scoring
    vague_words = ["thing", "stuff", "something", "maybe", "etc"]
    clarity = 8.0
    for w in vague_words:
        if re.search(rf"\b{w}\b", text, re.I):
            clarity -= 1.5
    if words < 5:
        clarity -= 3.0

    # Specificity scoring
    specificity = 5.0
    if any(q in text.lower() for q in ["return", "format", "must", "only", "json", "markdown", "table"]):
        specificity += 2.0
    if re.search(r"\b\d+\b", text):
        specificity += 1.0

    # Context scoring
    context = 4.0
    if any(c in text.lower() for c in ["because", "in order to", "repo", "using", "framework", "version"]):
        context += 3.0

    # Completeness scoring
    completeness = 5.0
    if any(k in text.lower() for k in ["role:", "task:", "context:", "goal:", "steps:"]):
        completeness += 3.0
    elif words > 20:
        completeness += 1.5

    # Structure scoring
    structure = 5.0
    if "\n" in text:
        structure += 2.0
    if any(line.strip().startswith(("-", "*", "1.")) for line in text.splitlines()):
        structure += 2.0

    def _clamp(v: float) -> float:
        return max(1.0, min(10.0, round(v, 1)))

    return RubricScore(
        clarity=_clamp(clarity),
        specificity=_clamp(specificity),
        context=_clamp(context),
        completeness=_clamp(completeness),
        structure=_clamp(structure),
    )

def render_rubric_table(score: RubricScore) -> str:
    lines = [
        "| Dimension    | Score (1-10) | Evaluation Band |",
        "|--------------|--------------|-----------------|",
        f"| Clarity      | {score.clarity:<12} | {'Solid' if score.clarity>=7 else 'Underspecified'} |",
        f"| Specificity  | {score.specificity:<12} | {'Solid' if score.specificity>=7 else 'Underspecified'} |",
        f"| Context      | {score.context:<12} | {'Solid' if score.context>=7 else 'Underspecified'} |",
        f"| Completeness | {score.completeness:<12} | {'Solid' if score.completeness>=7 else 'Underspecified'} |",
        f"| Structure    | {score.structure:<12} | {'Solid' if score.structure>=7 else 'Underspecified'} |",
        "|--------------|--------------|-----------------|",
        f"| **Overall**  | **{score.overall}**      | {'Production Ready' if score.overall>=8 else 'Needs Framework'} |",
    ]
    return "\n".join(lines)
```

Create `prompt_eng/studio/diff.py`:
```python
"""Terminal diff comparator showing changes between original and improved prompt."""
import difflib

def compare_prompt_diff(before: str, after: str) -> str:
    before_lines = before.splitlines(keepends=True)
    after_lines = after.splitlines(keepends=True)
    diff = difflib.unified_diff(before_lines, after_lines, fromfile="Original Prompt", tofile="Optimized Prompt")

    result = []
    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            result.append(f"\033[32m{line.rstrip()}\033[0m")  # Green
        elif line.startswith("-") and not line.startswith("---"):
            result.append(f"\033[31m{line.rstrip()}\033[0m")  # Red
        elif line.startswith("@@"):
            result.append(f"\033[36m{line.rstrip()}\033[0m")  # Cyan
        else:
            result.append(line.rstrip())
    return "\n".join(result)
```

Create `prompt_eng/studio/catalog.py`:
```python
"""Cross-repo prompt catalog query engine."""
from pathlib import Path
from typing import Any, Dict, List
from prompt_eng.models import parse_frontmatter_markdown

def query_prompt_catalog(repos_dir: Path, query: str) -> List[Dict[str, Any]]:
    matches = []
    q = query.lower()

    if not repos_dir.exists():
        return matches

    for repo_dir in repos_dir.iterdir():
        if not repo_dir.is_dir():
            continue
        prompts_dir = repo_dir / "prompts"
        if not prompts_dir.exists():
            continue

        for p_file in prompts_dir.glob("*.md"):
            try:
                content = p_file.read_text(encoding="utf-8", errors="ignore")
                meta, body = parse_frontmatter_markdown(content)
                haystack = f"{repo_dir.name} {p_file.name} {meta} {body}".lower()
                if q in haystack or not q:
                    matches.append({
                        "repo": repo_dir.name,
                        "file": p_file.name,
                        "path": str(p_file),
                        "framework": meta.get("framework", "N/A"),
                        "overall_score": meta.get("score", {}).get("overall", "N/A") if isinstance(meta.get("score"), dict) else "N/A",
                        "preview": body.strip()[:100] + "...",
                    })
            except Exception:
                continue

    return matches
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_studio.py -v`  
Expected: PASS with 3 tests ok.

- [ ] **Step 5: Commit**

```bash
git add prompt_eng/studio/ tests/test_studio.py
git commit -m "feat: implement studio utilities for rubric scoring, diffing, and catalog search"
```

---

### Task 6: CLI Command Router & Integration

**Files:**
- Create: `prompt_eng/cli.py`
- Modify: `bin/prompt-eng`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: `scanner`, `transcripts.resolver`, `studio.scorer`, `diff`, `catalog`, `models`
- Produces: CLI interface supporting: `scan`, `transcript`, `profile`, `score`, `diff`, `list`, `search`, `save-prompt`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cli.py
import subprocess
import sys
import unittest
from pathlib import Path

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent
        self.bin = self.root / "bin" / "prompt-eng"

    def run_cli(self, args):
        return subprocess.run([sys.executable, str(self.bin)] + args, capture_output=True, text=True)

    def test_help_command(self):
        res = self.run_cli(["--help"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("scan", res.stdout)
        self.assertIn("transcript", res.stdout)
        self.assertIn("score", res.stdout)

    def test_score_command(self):
        res = self.run_cli(["score", "Write a python unit test for auth middleware"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("Clarity", res.stdout)
        self.assertIn("Overall", res.stdout)

    def test_list_command(self):
        res = self.run_cli(["list"])
        self.assertEqual(res.returncode, 0)

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_cli.py -v`  
Expected: FAIL with missing subcommands in `prompt_eng/cli.py`

- [ ] **Step 3: Write minimal implementation**

Create `prompt_eng/cli.py`:
```python
"""Central CLI router for prompt-engineer hub."""
import argparse
import sys
from pathlib import Path
from prompt_eng.models import dump_frontmatter_markdown
from prompt_eng.scanner import scan_all_repositories
from prompt_eng.transcripts.resolver import SessionResolver, render_session_summary_markdown
from prompt_eng.studio.scorer import evaluate_rubric, render_rubric_table
from prompt_eng.studio.diff import compare_prompt_diff
from prompt_eng.studio.catalog import query_prompt_catalog

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="prompt-eng",
        description="Centralized Prompt Engineering Studio & Multi-Repo Hub CLI",
    )
    subparsers = parser.add_subparsers(dest="command", help="Studio commands")

    # scan command
    p_scan = subparsers.add_parser("scan", help="Scan /home/rizz/dev/* repositories and generate profiles")
    p_scan.add_argument("--root", default="/home/rizz/dev", help="Root directory containing target repos")

    # transcript command
    p_trans = subparsers.add_parser("transcript", help="Extract and summarize session transcript")
    p_trans.add_argument("--repo", required=True, help="Target repository name")
    p_trans.add_argument("--session", help="Specific conversation ID or session name")
    p_trans.add_argument("--file", help="Explicit path to JSONL log file")

    # profile command
    p_prof = subparsers.add_parser("profile", help="Display profile for a target repository")
    p_prof.add_argument("repo", help="Repository name")

    # score command
    p_score = subparsers.add_parser("score", help="Evaluate prompt against 5-dimension rubric")
    p_score.add_argument("text", nargs="?", help="Prompt text to score")
    p_score.add_argument("--file", help="File containing prompt to score")

    # diff command
    p_diff = subparsers.add_parser("diff", help="Compare original vs optimized prompt")
    p_diff.add_argument("before", help="Path to original prompt file or string")
    p_diff.add_argument("after", help="Path to optimized prompt file or string")

    # list command
    p_list = subparsers.add_parser("list", help="List tracked repositories and prompts")

    # search command
    p_search = subparsers.add_parser("search", help="Search prompt catalog across repos")
    p_search.add_argument("query", help="Keyword or framework to search")

    # save-prompt command
    p_save = subparsers.add_parser("save-prompt", help="Save engineered prompt with frontmatter")
    p_save.add_argument("--repo", required=True, help="Target repo name")
    p_save.add_argument("--name", required=True, help="Prompt slug name")
    p_save.add_argument("--framework", required=True, help="Prompt framework used (e.g. RISEN, CO-STAR)")
    p_save.add_argument("--content", help="Prompt body string")
    p_save.add_argument("--file", help="File containing prompt body")

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0

    app_root = Path(__file__).resolve().parent.parent
    repos_dir = app_root / "repos"

    if args.command == "scan":
        dev_root = Path(args.root)
        print(f"Scanning target repositories in {dev_root}...")
        profiles = scan_all_repositories(dev_root, repos_dir)
        print(f"✓ Successfully scanned and updated {len(profiles)} repository profiles in {repos_dir}/")
        return 0

    if args.command == "transcript":
        file_path = Path(args.file) if args.file else None
        try:
            summary = SessionResolver.resolve_session(args.repo, session_id=args.session, file_path=file_path)
            print(render_session_summary_markdown(summary))
            return 0
        except Exception as e:
            print(f"Error resolving session: {e}", file=sys.stderr)
            return 1

    if args.command == "profile":
        prof_file = repos_dir / args.repo / "profile.yaml"
        if not prof_file.exists():
            print(f"Profile for '{args.repo}' not found. Run 'prompt-eng scan' first.", file=sys.stderr)
            return 1
        print(prof_file.read_text(encoding="utf-8"))
        return 0

    if args.command == "score":
        text = args.text or ""
        if args.file and Path(args.file).exists():
            text = Path(args.file).read_text(encoding="utf-8")
        if not text:
            print("Error: Must provide prompt text or --file", file=sys.stderr)
            return 1
        score = evaluate_rubric(text)
        print(render_rubric_table(score))
        return 0

    if args.command == "diff":
        b_text = Path(args.before).read_text(encoding="utf-8") if Path(args.before).exists() else args.before
        a_text = Path(args.after).read_text(encoding="utf-8") if Path(args.after).exists() else args.after
        print(compare_prompt_diff(b_text, a_text))
        return 0

    if args.command == "list":
        results = query_prompt_catalog(repos_dir, "")
        repo_names = sorted([d.name for d in repos_dir.iterdir() if d.is_dir()]) if repos_dir.exists() else []
        print(f"=== Tracked Repositories ({len(repo_names)}) ===")
        for name in repo_names:
            p_count = len(list((repos_dir / name / "prompts").glob("*.md"))) if (repos_dir / name / "prompts").exists() else 0
            print(f"- {name:<20} ({p_count} prompts)")
        print(f"\nTotal Prompts in Catalog: {len(results)}")
        return 0

    if args.command == "search":
        matches = query_prompt_catalog(repos_dir, args.query)
        print(f"Found {len(matches)} prompt(s) matching '{args.query}':\n")
        for m in matches:
            print(f"[{m['repo']}] {m['file']} (FW: {m['framework']}, Score: {m['overall_score']})")
            print(f"  {m['preview']}\n")
        return 0

    if args.command == "save-prompt":
        body = args.content or ""
        if args.file and Path(args.file).exists():
            body = Path(args.file).read_text(encoding="utf-8")
        if not body:
            print("Error: Must provide prompt content or --file", file=sys.stderr)
            return 1

        target_dir = repos_dir / args.repo / "prompts"
        target_dir.mkdir(parents=True, exist_ok=True)
        slug = args.name if args.name.endswith(".md") else f"{args.name}.md"
        out_file = target_dir / slug

        score = evaluate_rubric(body)
        meta = {
            "name": args.name,
            "repo": args.repo,
            "framework": args.framework,
            "score": {
                "clarity": score.clarity,
                "specificity": score.specificity,
                "context": score.context,
                "completeness": score.completeness,
                "structure": score.structure,
                "overall": score.overall,
            },
        }
        out_file.write_text(dump_frontmatter_markdown(meta, body), encoding="utf-8")
        print(f"✓ Saved engineered prompt to {out_file}")
        return 0

    return 0
```

Update `bin/prompt-eng` to cleanly dispatch to `prompt_eng.cli`:
```python
#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from prompt_eng.cli import main

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_cli.py -v`  
Expected: PASS with 3 tests ok.

- [ ] **Step 5: Commit**

```bash
git add prompt_eng/cli.py bin/prompt-eng tests/test_cli.py
git commit -m "feat: connect full studio suite subcommands to cli router"
```

---

### Task 7: Embedded Skill Shadowing & Agent Studio Guidelines

**Files:**
- Create: `.agents/skills.json`
- Create: `.agents/skills/prompt-architect/` (cloned from `/home/rizz/.gemini/config/skills/prompt-architect/`)
- Create: `.claude/skills/prompt-architect/` (mirrored for Claude Code)
- Create: `AGENTS.md`
- Create: `CLAUDE.md`
- Test: `tests/test_skills_setup.py`

**Interfaces:**
- Consumes: Global `prompt-architect` assets from `/home/rizz/.gemini/config/skills/prompt-architect/`
- Produces: Local workspace-shadowed skills and standardized agent SOPs.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_skills_setup.py
import json
import unittest
from pathlib import Path

class TestSkillsSetup(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent

    def test_workspace_skills_json(self):
        skills_json = self.root / ".agents" / "skills.json"
        self.assertTrue(skills_json.exists())
        data = json.loads(skills_json.read_text(encoding="utf-8"))
        self.assertIn("entries", data)
        self.assertEqual(data["entries"][0]["path"], ".agents/skills")

    def test_local_skill_shadowing_files(self):
        ag_skill = self.root / ".agents" / "skills" / "prompt-architect" / "SKILL.md"
        cl_skill = self.root / ".claude" / "skills" / "prompt-architect" / "SKILL.md"
        self.assertTrue(ag_skill.exists(), "Antigravity local skill missing")
        self.assertTrue(cl_skill.exists(), "Claude Code local skill missing")

        content = ag_skill.read_text(encoding="utf-8")
        self.assertIn("name: prompt-architect", content)

    def test_instruction_files_contain_sop(self):
        ag_md = self.root / "AGENTS.md"
        cl_md = self.root / "CLAUDE.md"
        self.assertTrue(ag_md.exists())
        self.assertTrue(cl_md.exists())
        self.assertIn("prompt-eng", ag_md.read_text(encoding="utf-8"))
        self.assertIn("prompt-eng", cl_md.read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_skills_setup.py -v`  
Expected: FAIL with missing `.agents/skills.json` and local skill files.

- [ ] **Step 3: Write minimal implementation**

Create `.agents/skills.json`:
```json
{
  "entries": [
    {
      "path": ".agents/skills"
    }
  ]
}
```

Copy the global skill locally into both `.agents/skills/prompt-architect/` and `.claude/skills/prompt-architect/`:
```bash
mkdir -p .agents/skills .claude/skills
cp -r /home/rizz/.gemini/config/skills/prompt-architect .agents/skills/
cp -r /home/rizz/.gemini/config/skills/prompt-architect .claude/skills/
```

Create `AGENTS.md`:
```markdown
# Central Prompt Engineering Studio & Hub (Antigravity Instructions)

Welcome to the Prompt Engineering Hub for `/home/rizz/dev/`. As an AI pair programmer operating in this workspace, you serve as the **Prompt Studio Architect**.

## Core Operational SOP (4-Stage Lifecycle)

1. **Target Repo Context Discovery**:
   - Check if the target repo has been profiled in `repos/<repo-name>/profile.yaml`.
   - If not present or outdated, run `bin/prompt-eng scan`.
   - Read the target repo's invariants, instructions, and stack before authoring prompts.

2. **Session Transcript Ingestion**:
   - Pull the context of the user's active or recent conversation turn in the target repo:
     `bin/prompt-eng transcript --repo <target-repo> [--session <id>]`
   - Use this context snapshot (goals, tool actions, error messages) to tailor the prompt.

3. **Prompt Architecture Lifecycle**:
   - Assess the initial prompt using the 5-dimension rubric: `bin/prompt-eng score "<prompt>"`
   - Always resolve and execute the local workspace skill at `.agents/skills/prompt-architect/SKILL.md`. Never use or modify the global skill in `~/.gemini/config/skills/`.
   - Select the optimal framework (e.g. RISEN, CO-STAR, ReAct, BAB, Chain-of-Thought) and ask targeted clarifying questions.
   - Show the visual diff: `bin/prompt-eng diff <original_file> <improved_file>`.

4. **Persistence & Clean Presentation**:
   - Save the engineered prompt with frontmatter:
     `bin/prompt-eng save-prompt --repo <target-repo> --name <slug> --framework <fw> --file <prompt_file>`
   - Present the final clean prompt inside triple backticks with no scaffolding headers, so the user can easily copy and paste it into their target session.

## Invariants
- **Repo Isolation**: Do NOT write files or run mutating commands directly in `/home/rizz/dev/<other-repo>/`. Everything stays in `prompt-engineer/`.
- **Skill Shadowing**: The local `.agents/skills/prompt-architect/` is the single source of truth for this repo.
```

Create `CLAUDE.md`:
```markdown
# Central Prompt Engineering Studio & Hub (Claude Code Instructions)

Welcome to the Prompt Engineering Hub for `/home/rizz/dev/`.

## Tooling & Commands
- Fast offline tests: `python3 -m unittest discover -s tests`
- Multi-repo scan: `bin/prompt-eng scan`
- Transcript ingestion: `bin/prompt-eng transcript --repo <name>`
- Rubric scoring: `bin/prompt-eng score "<prompt>"`
- Diff comparison: `bin/prompt-eng diff <before> <after>`
- Catalog search: `bin/prompt-eng search <query>`

## Skill Shadowing
- For `prompt-architect`, use the local workspace skill in `.claude/skills/prompt-architect/SKILL.md`.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_skills_setup.py -v`  
Expected: PASS with 3 tests ok.

- [ ] **Step 5: Commit**

```bash
git add .agents/ .claude/ AGENTS.md CLAUDE.md tests/test_skills_setup.py
git commit -m "feat: embed workspace-shadowed prompt-architect skills and studio SOPs"
```

---

### Task 8: End-to-End System Smoke Test & Initial Live Workspace Scan

**Files:**
- Create: `tests/test_e2e.py`
- Create: `README.md`
- Output: `repos/*/profile.yaml` (from live initial scan)

**Interfaces:**
- Consumes: Entire system (`bin/prompt-eng`, `/home/rizz/dev/*`)
- Produces: Verified live scan across all repositories and comprehensive `README.md`.

- [ ] **Step 1: Write the failing E2E test**

```python
# tests/test_e2e.py
import subprocess
import sys
import unittest
from pathlib import Path

class TestE2E(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent
        self.bin = self.root / "bin" / "prompt-eng"

    def test_e2e_scan_and_profile_flow(self):
        # Run scan on dev root
        res_scan = subprocess.run([sys.executable, str(self.bin), "scan", "--root", "/home/rizz/dev"], capture_output=True, text=True)
        self.assertEqual(res_scan.returncode, 0, f"Scan failed: {res_scan.stderr}")

        # Verify repos directory has profiles
        repos_dir = self.root / "repos"
        self.assertTrue(repos_dir.exists())
        self.assertTrue((repos_dir / "0x-arbiter" / "profile.yaml").exists())

        # Test listing
        res_list = subprocess.run([sys.executable, str(self.bin), "list"], capture_output=True, text=True)
        self.assertEqual(res_list.returncode, 0)
        self.assertIn("0x-arbiter", res_list.stdout)

        # Test profile inspection
        res_prof = subprocess.run([sys.executable, str(self.bin), "profile", "0x-arbiter"], capture_output=True, text=True)
        self.assertEqual(res_prof.returncode, 0)
        self.assertIn("language: python", res_prof.stdout)

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails (before live scan)**

Run: `python3 -m unittest tests/test_e2e.py -v`  
Expected: FAIL with `AssertionError: False is not true` (profile.yaml not yet generated for 0x-arbiter)

- [ ] **Step 3: Execute initial live scan & generate comprehensive README.md**

Run: `python3 bin/prompt-eng scan --root /home/rizz/dev`

Create `README.md`:
```markdown
# 🏛️ Prompt Engineer Hub & Studio

A centralized studio and multi-repo hub to manage, engineer, evaluate, and catalog prompts across all repositories in `/home/rizz/dev/`.

## 🌟 Key Capabilities

- **Automated Repository Profiling**: Detects tech stacks, package managers, test runners, linters, and instruction files (`AGENTS.md`, `CLAUDE.md`) for all projects in `/home/rizz/dev/*`.
- **Multi-Harness Transcript Extraction**: Extracts compact, token-efficient session summaries (user goal, tools executed, errors encountered, last conversation turn) from Antigravity, Antigravity CLI, Antigravity IDE, and Claude Code.
- **Local Skill Shadowing (`prompt-architect`)**: Embedded locally in `.agents/skills/prompt-architect/` and `.claude/skills/prompt-architect/` so local adjustments remain isolated without modifying global machine skills.
- **Full Studio Suite CLI (`prompt-eng`)**:
  - `prompt-eng scan`: Pindai seluruh repo `/dev/*` dan hasilkan profil `repos/<name>/profile.yaml`.
  - `prompt-eng transcript --repo <name>`: Ekstrak ringkasan sesi aktif.
  - `prompt-eng score "<prompt>"`: Hitung skor rubrik 5-dimensi (Clarity, Specificity, Context, Completeness, Structure).
  - `prompt-eng diff <before> <after>`: Visualisasi perbandingan prompt berwarna di terminal.
  - `prompt-eng list` & `prompt-eng search <query>`: Katalog dan pencarian prompt lintas-repo.
  - `prompt-eng save-prompt`: Simpan prompt terstruktur dengan YAML frontmatter.

## 🚀 Quickstart

```bash
# 1. Pindai seluruh repositori di /home/rizz/dev/
bin/prompt-eng scan

# 2. Lihat profil repo target
bin/prompt-eng profile 0x-arbiter

# 3. Evaluasi skor prompt
bin/prompt-eng score "Fix auth middleware to use bearer token"

# 4. Ekstrak transkrip sesi terakhir
bin/prompt-eng transcript --repo 0x-arbiter

# 5. Jalankan unit test
python3 -m unittest discover -s tests
```

## 📐 Architecture & Standards
Detailed design specifications are available in [`docs/superpowers/specs/2026-09-22-prompt-engineer-hub-design.md`](docs/superpowers/specs/2026-09-22-prompt-engineer-hub-design.md).
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_e2e.py -v && python3 -m unittest discover -s tests`  
Expected: PASS with 100% of tests passing.

- [ ] **Step 5: Commit**

```bash
git add README.md tests/test_e2e.py repos/
git commit -m "feat: complete initial live scan and e2e smoke verification"
```
