# Performance Enhancement & Open Source Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the Performance Enhancement Suite (`prompt-eng scaffold`, `prompt-eng lint`, workspace-scoped transcript resolver, filtered catalog search) and prepare the repository as a clean, public open-source project on GitHub under `0xrizz/prompt-engineer`.

**Architecture:** A modular, zero-dependency Python 3.14 architecture extending `prompt_eng` with four decoupled studio subsystems: transcript normalization, prompt scaffolding, invariant & framework linting, and multi-axis catalog filtering. The repository is hardened for open-source publication with an MIT license, sanitized `.gitignore` ignoring local user profiles in `repos/`, and CI-ready linting/testing.

**Tech Stack:** Python 3.14, Hatchling, Pytest, Ruff, GitHub CLI (`gh`).

**Spec:** [`docs/superpowers/specs/2026-10-15-performance-enhancement-suite-design.md`](file:///home/rizz/dev/prompt-engineer/docs/superpowers/specs/2026-10-15-performance-enhancement-suite-design.md)

## Global Constraints

- **Runtime Dependency Invariant:** Zero external runtime dependencies in `pyproject.toml`. Everything must use the Python 3.14 standard library.
- **Fast Offline Tests:** All tests run offline via `uv run pytest tests/` with 100% pass rate and target duration < 2.5s.
- **Linter & Formatter:** Clean passes on `uv run ruff check .` and `uv run ruff format --check .`.
- **Repo Isolation:** All mutating actions stay strictly within `/home/rizz/dev/prompt-engineer/`. Local dev repos in `/home/rizz/dev/` are read-only references.
- **Privacy & Git Hygiene:** Local profiles in `repos/*` are ignored in git; only `repos/.gitkeep` and `repos/example-repo/` are committed.

---

### Task 1: Expand Data Models for Linting & Diagnostics

**Files:**
- Modify: `prompt_eng/models.py`
- Modify: `tests/test_models.py`

**Interfaces:**
- Produces: `LintIssue` dataclass (`severity: str`, `rule_id: str`, `message: str`, `suggestion: str = ""`)
- Produces: `LintReport` dataclass (`repo: str`, `prompt_name: str`, `is_valid: bool`, `issues: list[LintIssue]`) with properties `has_errors: bool` and `has_warnings: bool`

- [ ] **Step 1: Write failing test in `tests/test_models.py`**

Add to `tests/test_models.py`:

```python
from prompt_eng.models import LintIssue, LintReport


def test_lint_issue_and_report_dataclasses():
    issue_err = LintIssue(
        severity="ERROR",
        rule_id="RULE-INV-001",
        message="Violates package hallucination invariant",
        suggestion="Remove unmanifested package import",
    )
    issue_warn = LintIssue(
        severity="WARNING",
        rule_id="RULE-RUBRIC-001",
        message="Low clarity score (5.5)",
        suggestion="Elaborate ambiguous pronouns",
    )
    report = LintReport(
        repo="0x-arbiter",
        prompt_name="sprint-01",
        is_valid=False,
        issues=[issue_err, issue_warn],
    )
    assert report.has_errors is True
    assert report.has_warnings is True
    assert report.is_valid is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_models.py -k test_lint_issue_and_report_dataclasses -v`  
Expected: FAIL with `ImportError: cannot import name 'LintIssue' from 'prompt_eng.models'`

- [ ] **Step 3: Implement `LintIssue` and `LintReport` in `prompt_eng/models.py`**

Append to `prompt_eng/models.py`:

```python
@dataclass
class LintIssue:
    severity: str  # "ERROR" | "WARNING"
    rule_id: str
    message: str
    suggestion: str = ""


@dataclass
class LintReport:
    repo: str
    prompt_name: str
    is_valid: bool
    issues: list[LintIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "ERROR" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == "WARNING" for i in self.issues)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_models.py -k test_lint_issue_and_report_dataclasses -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add prompt_eng/models.py tests/test_models.py
git commit -m "feat(models): add LintIssue and LintReport data models"
```

---

### Task 2: Workspace-Aware Transcript Resolver & XML Sanitization

**Files:**
- Modify: `prompt_eng/transcripts/antigravity.py`
- Modify: `prompt_eng/transcripts/resolver.py`
- Modify: `tests/test_transcripts.py`

**Interfaces:**
- Consumes: Antigravity and Claude Code transcript logs on disk
- Produces: Cleaned `user_goal` (stripped of `<USER_REQUEST>`, `<ADDITIONAL_METADATA>`, `<USER_SETTINGS_CHANGE>`)
- Produces: Non-empty `last_turn_state` by traversing back to latest substantive assistant message
- Produces: `SessionResolver.find_latest_session(repo_name)` scoped to sessions referencing `/home/rizz/dev/<repo_name>`

- [ ] **Step 1: Write failing tests for XML sanitization and repo-scoped session finding in `tests/test_transcripts.py`**

Append to `tests/test_transcripts.py`:

```python
def test_parse_antigravity_xml_sanitization():
    raw_content = (
        "<USER_REQUEST>\n"
        "Implement authentication middleware\n"
        "</USER_REQUEST>\n"
        "<ADDITIONAL_METADATA>\n"
        "The current local time is: 2026-10-15T12:00:00+07:00\n"
        "</ADDITIONAL_METADATA>\n"
        "<USER_SETTINGS_CHANGE>\n"
        "Model changed\n"
        "</USER_SETTINGS_CHANGE>"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
        f.write(
            json.dumps({"type": "USER_INPUT", "content": raw_content}) + "\n"
        )
        f.write(
            json.dumps(
                {
                    "type": "PLANNER_RESPONSE",
                    "content": "I have created the auth middleware class.",
                }
            )
            + "\n"
        )
        tmp_path = Path(f.name)

    try:
        summary = parse_antigravity_transcript(tmp_path, repo_name="sample-repo")
        assert summary.user_goal == "Implement authentication middleware"
        assert "ADDITIONAL_METADATA" not in summary.user_goal
        assert "I have created the auth middleware class." in summary.last_turn_state
    finally:
        tmp_path.unlink()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_transcripts.py -k test_parse_antigravity_xml_sanitization -v`  
Expected: FAIL because `<USER_REQUEST>` and `<ADDITIONAL_METADATA>` are present in `summary.user_goal`.

- [ ] **Step 3: Implement XML sanitization and turn recovery in `prompt_eng/transcripts/antigravity.py` and workspace filtering in `resolver.py`**

In `prompt_eng/transcripts/antigravity.py`:
Add a helper `_clean_user_input(text: str) -> str`:
```python
def _clean_user_input(text: str) -> str:
    """Extract core intent from <USER_REQUEST> if present, removing harness metadata."""
    req_match = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", text, re.DOTALL)
    if req_match:
        return req_match.group(1).strip()
    # Strip metadata blocks if present without user request tag
    cleaned = re.sub(
        r"<(ADDITIONAL_METADATA|USER_SETTINGS_CHANGE|SKILL)>.*?</\1>",
        "",
        text,
        flags=re.DOTALL,
    )
    return cleaned.strip()
```
And use it when `entry_type == "USER_INPUT"`:
```python
if entry_type == "USER_INPUT" and not user_goal:
    user_goal = _clean_user_input(str(content))
```
And when `entry_type == "PLANNER_RESPONSE"`:
```python
if entry_type == "PLANNER_RESPONSE":
    text_content = str(content).strip() if content else ""
    if not text_content and "thinking" in entry and entry["thinking"]:
        text_content = str(entry["thinking"]).strip()
    if text_content:
        last_turn_state = text_content[:300]
```

In `prompt_eng/transcripts/resolver.py`:
In `find_latest_session(repo_name: str, target_dir: Path | None = None)`:
When inspecting Claude projects, filter candidate directories matching `repo_name`:
```python
claude_projects = Path.home() / ".claude" / "projects"
if claude_projects.exists():
    cl_candidates = []
    for p_dir in claude_projects.iterdir():
        if p_dir.is_dir() and repo_name in p_dir.name:
            cl_candidates.extend(p_dir.glob("*.jsonl"))
    if cl_candidates:
        cl_candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return "claude-code", cl_candidates[0]
```
When inspecting Antigravity brain, look for sessions that contain references to `repo_name`:
```python
ag_brain = Path.home() / ".gemini" / "antigravity" / "brain"
if ag_brain.exists():
    sessions = sorted(
        ag_brain.glob("*/.system_generated/logs/transcript.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    # Filter sessions matching target repo in transcript content or Cwd
    if repo_name:
        for s in sessions[:30]:  # check top 30 recent sessions
            try:
                # inspect first 50 lines for repo footprint
                with open(s, "r", encoding="utf-8") as f:
                    sample = "".join(f.readline() for _ in range(50))
                if f"/dev/{repo_name}" in sample or f'"{repo_name}"' in sample:
                    return "antigravity", s
            except OSError:
                continue
    if sessions:
        return "antigravity", sessions[0]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_transcripts.py -v`  
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add prompt_eng/transcripts/antigravity.py prompt_eng/transcripts/resolver.py tests/test_transcripts.py
git commit -m "feat(transcripts): add XML sanitization and repo-scoped session resolver"
```

---

### Task 3: Implement Prompt Scaffolder Engine (`prompt_eng/studio/scaffolder.py`)

**Files:**
- Create: `prompt_eng/studio/scaffolder.py`
- Create: `tests/test_scaffolder.py`

**Interfaces:**
- Consumes: `RepoProfile` (from `repos/<repo>/profile.yaml` or scanned repo)
- Produces: `scaffold_prompt(repo_profile: RepoProfile | None, repo_name: str, prompt_name: str, framework: str) -> tuple[dict[str, Any], str]`
- Produces: Formatted prompt markdown containing frontmatter with initialized score and populated framework sections

- [ ] **Step 1: Write failing test in `tests/test_scaffolder.py`**

Create `tests/test_scaffolder.py`:

```python
from pathlib import Path
import unittest

from prompt_eng.models import HarnessInfo, RepoProfile, StackInfo
from prompt_eng.studio.scaffolder import scaffold_prompt


class TestScaffolder(unittest.TestCase):
    def setUp(self):
        self.profile = RepoProfile(
            name="py-service",
            path="/home/rizz/dev/py-service",
            description="High throughput indexing service",
            stack=StackInfo(
                language="Python",
                package_manager="uv",
                test_framework="pytest",
                linter="ruff",
            ),
            harness=HarnessInfo(
                instruction_files=["AGENTS.md"],
                active_skills=["prompt-architect"],
                rules=["safety.md"],
            ),
            invariants=[
                "Fast offline unit tests: uv run pytest tests/",
                "No unmanifested runtime packages",
            ],
            failure_gates=["Workflow Drift Gate"],
        )

    def test_scaffold_risen_framework(self):
        meta, body = scaffold_prompt(
            self.profile,
            repo_name="py-service",
            prompt_name="add-auth",
            framework="RISEN",
        )
        self.assertEqual(meta["name"], "add-auth")
        self.assertEqual(meta["repo"], "py-service")
        self.assertEqual(meta["framework"], "RISEN")
        self.assertIn("## Role", body)
        self.assertIn("## Input", body)
        self.assertIn("## Steps", body)
        self.assertIn("## Expectation", body)
        self.assertIn("## Narrowing", body)
        self.assertIn("Fast offline unit tests", body)
        self.assertIn("Workflow Drift Gate", body)

    def test_scaffold_costar_framework(self):
        meta, body = scaffold_prompt(
            self.profile,
            repo_name="py-service",
            prompt_name="promo-copy",
            framework="CO-STAR",
        )
        self.assertEqual(meta["framework"], "CO-STAR")
        self.assertIn("## Context", body)
        self.assertIn("## Objective", body)
        self.assertIn("## Style", body)
        self.assertIn("## Tone", body)
        self.assertIn("## Audience", body)
        self.assertIn("## Response", body)

    def test_scaffold_without_profile(self):
        meta, body = scaffold_prompt(
            None,
            repo_name="unknown-repo",
            prompt_name="quick-fix",
            framework="BAB",
        )
        self.assertEqual(meta["framework"], "BAB")
        self.assertIn("## Before", body)
        self.assertIn("## After", body)
        self.assertIn("## Bridge", body)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_scaffolder.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'prompt_eng.studio.scaffolder'`

- [ ] **Step 3: Implement `scaffolder.py`**

Create `prompt_eng/studio/scaffolder.py`:

```python
"""Template scaffolding engine generating framework-structured prompts grounded in repo profile."""

from __future__ import annotations

from typing import Any

from prompt_eng.models import RepoProfile
from prompt_eng.studio.scorer import evaluate_rubric


def scaffold_prompt(
    profile: RepoProfile | None,
    repo_name: str,
    prompt_name: str,
    framework: str = "RISEN",
) -> tuple[dict[str, Any], str]:
    """Generate structured prompt markdown with frontmatter pre-populated with repo context."""
    fw = framework.upper()
    lang = profile.stack.language if profile and profile.stack else "Software"
    test_cmd = (
        f"{profile.stack.package_manager} run {profile.stack.test_framework}"
        if profile and profile.stack and profile.stack.package_manager and profile.stack.test_framework
        else "test runner"
    )

    invariants_text = ""
    if profile and profile.invariants:
        invariants_text += "\n".join(f"- {inv}" for inv in profile.invariants)
    if profile and profile.failure_gates:
        if invariants_text:
            invariants_text += "\n"
        invariants_text += "\n".join(f"- Guard against: {gate}" for gate in profile.failure_gates)
    if not invariants_text:
        invariants_text = "- Strictly follow repository coding conventions and test-first discipline."

    if fw == "RISEN":
        body = f"""## Role
You are a Principal {lang} Systems Engineer paired to execute tasks in `{repo_name}`.

## Input
- Target Milestone/Context: {profile.active_milestone if profile and profile.active_milestone else "Feature specification in workspace"}
- Repository: `{repo_name}` ({profile.description if profile else "Target workspace"})

## Steps
1. Write the minimal failing unit test verifying the required behavior using `{test_cmd}`.
2. Implement the clean production logic to satisfy the test assertions.
3. Verify formatting and linting pass with zero warnings.
4. Review diff to ensure no regression or scope creep.

## Expectation
- 100% passing tests with deterministic assertions.
- Complete type safety and preservation of existing docstrings.
- Clean git status with verified deliverables.

## Narrowing / Invariants
{invariants_text}
"""
    elif fw == "CO-STAR":
        body = f"""## Context
Repository `{repo_name}`: {profile.description if profile else "Production software repository"} ({lang} stack).

## Objective
Deliver a comprehensive, production-ready solution for `{prompt_name}`.

## Style
Concise, authoritative technical specification adhering strictly to established architectural boundaries.

## Tone
Direct, professional, evidence-based.

## Audience
Senior software engineers and autonomous agent pairs requiring explicit, unambiguous contracts.

## Response
A complete implementation with corresponding unit tests and verification output.

## Constraints & Invariants
{invariants_text}
"""
    elif fw == "BAB":
        body = f"""## Before
Current limitations or defects observed in `{repo_name}` for `{prompt_name}`.

## After
Desired state with verified functionality, full test coverage, and optimized performance.

## Bridge
Step-by-step technical plan to transition from Before to After:
1. Formulate test contract.
2. Refactor/implement core logic.
3. Validate against repository invariants:
{invariants_text}
"""
    elif fw == "REACT":
        body = f"""## System Instructions
You are operating in `{repo_name}` using the Thought-Action-Observation loop.

## Invariants & Guardrails
{invariants_text}

## Goal
Resolve `{prompt_name}` following the ReAct methodology:
- Thought: Reason about the immediate next step.
- Action: Invoke exact read/edit/test command (e.g. `{test_cmd}`).
- Observation: Analyze command output before proceeding.
"""
    else:  # Fallback to general structured prompt
        body = f"""## Role & Context
Operating within `{repo_name}` ({lang}).

## Instructions
Complete `{prompt_name}` following strict TDD discipline.

## Guardrails & Invariants
{invariants_text}
"""

    score = evaluate_rubric(body)
    meta: dict[str, Any] = {
        "name": prompt_name,
        "repo": repo_name,
        "framework": fw,
        "score": {
            "clarity": score.clarity,
            "specificity": score.specificity,
            "context": score.context,
            "completeness": score.completeness,
            "structure": score.structure,
            "overall": score.overall,
        },
    }
    return meta, body
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_scaffolder.py -v`  
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add prompt_eng/studio/scaffolder.py tests/test_scaffolder.py
git commit -m "feat(studio): implement prompt scaffolder with profile grounding"
```

---

### Task 4: Implement Invariant & Framework Linter (`prompt_eng/studio/linter.py`)

**Files:**
- Create: `prompt_eng/studio/linter.py`
- Create: `tests/test_linter.py`

**Interfaces:**
- Consumes: Prompt content (file or string), `RepoProfile` (from `profile.yaml`)
- Produces: `lint_prompt(prompt_text: str, profile: RepoProfile | None, framework: str = "", strict: bool = False) -> LintReport`
- Enforces:
  - `ERROR`: Invariant conflicts (e.g. `npm` in python project), missing framework sections
  - `WARNING`: Low rubric dimensions (<7.0), vague keywords, words < 25
  - `Exit Code`: 1 if errors or (warnings and strict), 0 otherwise

- [ ] **Step 1: Write failing tests in `tests/test_linter.py`**

Create `tests/test_linter.py`:

```python
import unittest

from prompt_eng.models import RepoProfile, StackInfo
from prompt_eng.studio.linter import lint_prompt


class TestLinter(unittest.TestCase):
    def setUp(self):
        self.profile = RepoProfile(
            name="py-service",
            path="/home/rizz/dev/py-service",
            description="Python service",
            stack=StackInfo(
                language="Python",
                package_manager="uv",
                test_framework="pytest",
                linter="ruff",
            ),
            invariants=[
                "Fast offline unit tests: uv run pytest tests/",
                "No unmanifested packages",
            ],
            failure_gates=["Workflow Drift"],
        )

    def test_lint_detects_toolchain_mismatch_error(self):
        bad_prompt = "Run npm install and execute npm test to check everything."
        report = lint_prompt(bad_prompt, self.profile, framework="RISEN")
        self.assertFalse(report.is_valid)
        self.assertTrue(report.has_errors)
        error_rules = [i.rule_id for i in report.issues if i.severity == "ERROR"]
        self.assertIn("ERR-TOOLCHAIN-MISMATCH", error_rules)

    def test_lint_detects_missing_framework_sections(self):
        incomplete_risen = "## Role\nEngineer\n## Input\nData\nSome stuff here."
        report = lint_prompt(incomplete_risen, self.profile, framework="RISEN")
        self.assertTrue(report.has_errors)
        error_rules = [i.rule_id for i in report.issues if i.severity == "ERROR"]
        self.assertIn("ERR-FRAMEWORK-INCOMPLETE", error_rules)

    def test_lint_detects_vague_words_warning(self):
        valid_risen = (
            "## Role\nStaff Engineer\n"
            "## Input\nSpecs\n"
            "## Steps\n1. Run tests\n"
            "## Expectation\nPass\n"
            "## Narrowing\nInvariants\n"
            "Maybe we should do something about that thing."
        )
        report = lint_prompt(valid_risen, self.profile, framework="RISEN")
        self.assertFalse(report.has_errors)
        self.assertTrue(report.has_warnings)
        warning_rules = [i.rule_id for i in report.issues if i.severity == "WARNING"]
        self.assertIn("WARN-VAGUE-LANGUAGE", warning_rules)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_linter.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'prompt_eng.studio.linter'`

- [ ] **Step 3: Implement `linter.py`**

Create `prompt_eng/studio/linter.py`:

```python
"""Linting engine enforcing target repository invariants, framework completeness, and rubric standards."""

from __future__ import annotations

import re

from prompt_eng.models import LintIssue, LintReport, RepoProfile
from prompt_eng.studio.scorer import evaluate_rubric


def lint_prompt(
    prompt_text: str,
    profile: RepoProfile | None = None,
    framework: str = "",
    prompt_name: str = "prompt",
) -> LintReport:
    """Evaluate prompt against repository invariants, framework structure, and rubric thresholds."""
    issues: list[LintIssue] = []
    text = prompt_text.strip()
    fw = framework.upper() if framework else ""

    # 1. Framework Completeness Checks (ERROR)
    if fw == "RISEN":
        required = ["Role", "Input", "Steps", "Expectation", "Narrowing"]
        missing = [sec for sec in required if not re.search(rf"##\s+{sec}", text, re.IGNORECASE)]
        if missing:
            issues.append(
                LintIssue(
                    severity="ERROR",
                    rule_id="ERR-FRAMEWORK-INCOMPLETE",
                    message=f"RISEN prompt missing required section(s): {', '.join(missing)}",
                    suggestion=f"Add ## {missing[0]} to ensure full framework compliance.",
                )
            )
    elif fw == "CO-STAR":
        required = ["Context", "Objective", "Style", "Tone", "Audience", "Response"]
        missing = [sec for sec in required if not re.search(rf"##\s+{sec}", text, re.IGNORECASE)]
        if missing:
            issues.append(
                LintIssue(
                    severity="ERROR",
                    rule_id="ERR-FRAMEWORK-INCOMPLETE",
                    message=f"CO-STAR prompt missing required section(s): {', '.join(missing)}",
                    suggestion=f"Add ## {missing[0]} to structure the prompt.",
                )
            )
    elif fw == "BAB":
        required = ["Before", "After", "Bridge"]
        missing = [sec for sec in required if not re.search(rf"##\s+{sec}", text, re.IGNORECASE)]
        if missing:
            issues.append(
                LintIssue(
                    severity="ERROR",
                    rule_id="ERR-FRAMEWORK-INCOMPLETE",
                    message=f"BAB prompt missing required section(s): {', '.join(missing)}",
                    suggestion="Add ## Before, ## After, and ## Bridge sections.",
                )
            )

    # 2. Toolchain & Invariant Checks (ERROR)
    if profile and profile.stack:
        lang = profile.stack.language.lower() if profile.stack.language else ""
        if "python" in lang:
            if re.search(r"\b(npm|yarn|pnpm|bun)\b", text, re.IGNORECASE):
                issues.append(
                    LintIssue(
                        severity="ERROR",
                        rule_id="ERR-TOOLCHAIN-MISMATCH",
                        message=f"Prompt references Node package managers in a Python project (`{profile.name}`)",
                        suggestion="Replace references with uv/python/pytest.",
                    )
                )
        elif any(js_lang in lang for js_lang in ["node", "javascript", "typescript"]):
            if re.search(r"\b(pip|pytest|uv run)\b", text, re.IGNORECASE):
                issues.append(
                    LintIssue(
                        severity="ERROR",
                        rule_id="ERR-TOOLCHAIN-MISMATCH",
                        message=f"Prompt references Python tools in a JS/TS project (`{profile.name}`)",
                        suggestion="Replace references with npm/yarn/pnpm/vitest.",
                    )
                )

    # 3. Rubric & Vague Language Checks (WARNING)
    vague_matches = [
        w for w in ["thing", "stuff", "maybe", "something", "etc"] if re.search(rf"\b{w}\b", text, re.IGNORECASE)
    ]
    if vague_matches:
        issues.append(
            LintIssue(
                severity="WARNING",
                rule_id="WARN-VAGUE-LANGUAGE",
                message=f"Prompt contains ambiguous terms: {', '.join(vague_matches)}",
                suggestion="Replace with explicit nouns and exact technical identifiers.",
            )
        )

    score = evaluate_rubric(text)
    if score.overall is not None and score.overall < 7.0:
        issues.append(
            LintIssue(
                severity="WARNING",
                rule_id="WARN-LOW-RUBRIC-SCORE",
                message=f"Overall rubric score ({score.overall}/10) is below production threshold (7.0)",
                suggestion="Expand Context and Structure sections to improve rating.",
            )
        )

    is_valid = not any(i.severity == "ERROR" for i in issues)
    return LintReport(
        repo=profile.name if profile else "unknown",
        prompt_name=prompt_name,
        is_valid=is_valid,
        issues=issues,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_linter.py -v`  
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add prompt_eng/studio/linter.py tests/test_linter.py
git commit -m "feat(studio): implement prompt invariant and framework linter"
```

---

### Task 5: Upgrade Catalog Search with Multi-Axis Filtering & JSON Export

**Files:**
- Modify: `prompt_eng/studio/catalog.py`
- Create: `tests/test_catalog.py`

**Interfaces:**
- Consumes: `repos_dir`, `query`, and optional filters (`repo`, `framework`, `min_score`)
- Produces: Filtered list of prompt dictionaries including parsed scores and preview

- [ ] **Step 1: Write failing test in `tests/test_catalog.py`**

Create `tests/test_catalog.py`:

```python
from pathlib import Path
import tempfile
import unittest

from prompt_eng.models import dump_frontmatter_markdown
from prompt_eng.studio.catalog import query_prompt_catalog


class TestCatalogSearch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repos_dir = Path(self.tmp.name)

        # Setup Repo A
        (self.repos_dir / "repo-a" / "prompts").mkdir(parents=True)
        meta_a1 = {"name": "p1", "framework": "RISEN", "score": {"overall": 8.5}}
        meta_a2 = {"name": "p2", "framework": "CO-STAR", "score": {"overall": 6.0}}
        (self.repos_dir / "repo-a" / "prompts" / "p1.md").write_text(
            dump_frontmatter_markdown(meta_a1, "Execute authentication tests"),
            encoding="utf-8",
        )
        (self.repos_dir / "repo-a" / "prompts" / "p2.md").write_text(
            dump_frontmatter_markdown(meta_a2, "Create marketing promo copy"),
            encoding="utf-8",
        )

        # Setup Repo B
        (self.repos_dir / "repo-b" / "prompts").mkdir(parents=True)
        meta_b1 = {"name": "p3", "framework": "RISEN", "score": {"overall": 7.5}}
        (self.repos_dir / "repo-b" / "prompts" / "p3.md").write_text(
            dump_frontmatter_markdown(meta_b1, "Refactor database migrations"),
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_search_by_framework(self):
        results = query_prompt_catalog(self.repos_dir, "", framework="RISEN")
        self.assertEqual(len(results), 2)
        names = [r["file"] for r in results]
        self.assertIn("p1.md", names)
        self.assertIn("p3.md", names)

    def test_search_by_min_score(self):
        results = query_prompt_catalog(self.repos_dir, "", min_score=8.0)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["file"], "p1.md")

    def test_search_by_repo_filter(self):
        results = query_prompt_catalog(self.repos_dir, "", repo="repo-b")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["file"], "p3.md")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_catalog.py -v`  
Expected: FAIL with `TypeError: query_prompt_catalog() got an unexpected keyword argument 'framework'`

- [ ] **Step 3: Update `prompt_eng/studio/catalog.py`**

Update `query_prompt_catalog` in `prompt_eng/studio/catalog.py`:

```python
def query_prompt_catalog(
    repos_dir: Path,
    query: str,
    repo: str | None = None,
    framework: str | None = None,
    min_score: float | None = None,
) -> list[dict[str, Any]]:
    """Search for prompts across all repo prompt catalogs matching query and structured filters."""
    matches: list[dict[str, Any]] = []
    q = query.lower()

    if not repos_dir.exists():
        return matches

    for repo_dir in sorted(repos_dir.iterdir(), key=lambda p: p.name):
        if not repo_dir.is_dir():
            continue
        if repo and repo.lower() not in repo_dir.name.lower():
            continue

        prompts_dir = repo_dir / "prompts"
        if not prompts_dir.exists():
            continue

        for p_file in sorted(prompts_dir.glob("*.md"), key=lambda p: p.name):
            try:
                content = p_file.read_text(encoding="utf-8", errors="ignore")
                meta, body = parse_frontmatter_markdown(content)
                prompt_fw = str(meta.get("framework", "N/A"))
                if framework and framework.lower() not in prompt_fw.lower():
                    continue

                score_meta = meta.get("score")
                overall_score: float | str = (
                    score_meta.get("overall", "N/A") if isinstance(score_meta, dict) else "N/A"
                )
                if min_score is not None:
                    if not isinstance(overall_score, (int, float)) or overall_score < min_score:
                        continue

                haystack = f"{repo_dir.name} {p_file.name} {meta} {body}".lower()
                if q in haystack or not q:
                    matches.append(
                        {
                            "repo": repo_dir.name,
                            "file": p_file.name,
                            "path": str(p_file),
                            "framework": prompt_fw,
                            "overall_score": overall_score,
                            "preview": body.strip()[:100] + "...",
                        }
                    )
            except (OSError, ValueError, TypeError, KeyError):
                continue

    return matches
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_catalog.py -v`  
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add prompt_eng/studio/catalog.py tests/test_catalog.py
git commit -m "feat(catalog): add structured filters for framework, repo, and min_score"
```

---

### Task 6: Connect Subcommands `scaffold`, `lint`, and Enhanced `search` to CLI Router

**Files:**
- Modify: `prompt_eng/cli.py`
- Modify: `tests/test_cli.py`

**Interfaces:**
- Connects: `prompt-eng scaffold --repo <r> --name <n> --framework <f> [--stdout]`
- Connects: `prompt-eng lint <file_or_text> --repo <r> [--strict]`
- Connects: `prompt-eng search [q] [--repo <r>] [--framework <f>] [--min-score <m>] [--json]`

- [ ] **Step 1: Write CLI integration tests in `tests/test_cli.py`**

Append to `tests/test_cli.py`:

```python
    def test_cli_scaffold_stdout(self):
        res = self.run_cli(["scaffold", "--repo", "sample-repo", "--name", "test-p", "--framework", "RISEN", "--stdout"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("## Role", res.stdout)
        self.assertIn("## Steps", res.stdout)

    def test_cli_lint_clean_and_strict(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("## Role\nEng\n## Input\nIn\n## Steps\n1. Go\n## Expectation\nPass\n## Narrowing\nNone\n")
            f_path = f.name
        try:
            res = self.run_cli(["lint", f_path, "--repo", "cli-sample"])
            self.assertEqual(res.returncode, 0)
            self.assertIn("✓ Lint passed", res.stdout)
        finally:
            Path(f_path).unlink()

    def test_cli_search_json(self):
        res = self.run_cli(["search", "", "--json"])
        self.assertEqual(res.returncode, 0)
        self.assertTrue(res.stdout.strip().startswith("[") or res.stdout.strip().startswith("{"))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py -k "test_cli_scaffold_stdout or test_cli_lint_clean_and_strict" -v`  
Expected: FAIL with unrecognized command `scaffold`

- [ ] **Step 3: Update `prompt_eng/cli.py`**

In `prompt_eng/cli.py`:
1. Add imports:
```python
from prompt_eng.studio.linter import lint_prompt
from prompt_eng.studio.scaffolder import scaffold_prompt
```
2. Add subparsers for `scaffold` and `lint`, and flags for `search`:
```python
    # scaffold
    p_scaffold = subparsers.add_parser("scaffold", help="Generate prompt template from repo profile")
    p_scaffold.add_argument("--repo", required=True, help="Target repository name")
    p_scaffold.add_argument("--name", required=True, help="Prompt name/slug")
    p_scaffold.add_argument("--framework", default="RISEN", help="Prompt framework (RISEN, CO-STAR, BAB, ReAct)")
    p_scaffold.add_argument("--stdout", action="store_true", help="Print generated prompt to stdout instead of saving file")

    # lint
    p_lint = subparsers.add_parser("lint", help="Lint prompt against repository invariants and framework rules")
    p_lint.add_argument("target", help="Prompt text or file path to lint")
    p_lint.add_argument("--repo", required=True, help="Target repository name for invariant checks")
    p_lint.add_argument("--framework", default="", help="Expected framework structure")
    p_lint.add_argument("--strict", action="store_true", help="Fail on any warning (exit code 1)")

    # update search parser
    p_search.add_argument("--repo", default=None, help="Filter by repository name")
    p_search.add_argument("--framework", default=None, help="Filter by framework")
    p_search.add_argument("--min-score", type=float, default=None, help="Filter by minimum overall score")
    p_search.add_argument("--json", action="store_true", help="Output results in JSON format")
```
3. Add handler for `scaffold`:
```python
    if args.command == "scaffold":
        profile_file = repos_dir / args.repo / "profile.yaml"
        profile = None
        if profile_file.exists():
            from prompt_eng.models import load_yaml_simple, RepoProfile, StackInfo, HarnessInfo
            loaded = load_yaml_simple(profile_file.read_text(encoding="utf-8"))
            st = loaded.get("stack", {})
            ha = loaded.get("harness", {})
            profile = RepoProfile(
                name=loaded.get("name", args.repo),
                path=loaded.get("path", ""),
                description=loaded.get("description", ""),
                stack=StackInfo(
                    language=st.get("language", ""),
                    package_manager=st.get("package_manager", ""),
                    test_framework=st.get("test_framework", ""),
                    linter=st.get("linter", ""),
                ),
                harness=HarnessInfo(
                    instruction_files=ha.get("instruction_files", []),
                    active_skills=ha.get("active_skills", []),
                    rules=ha.get("rules", []),
                ),
                invariants=loaded.get("invariants", []),
                failure_gates=loaded.get("failure_gates", []),
                active_milestone=loaded.get("active_milestone", ""),
            )

        meta, body = scaffold_prompt(profile, args.repo, args.name, args.framework)
        rendered = dump_frontmatter_markdown(meta, body)
        if args.stdout:
            print(rendered)
            return 0

        target_dir = repos_dir / args.repo / "prompts"
        target_dir.mkdir(parents=True, exist_ok=True)
        slug = args.name if args.name.endswith(".md") else f"{args.name}.md"
        out_file = target_dir / slug
        out_file.write_text(rendered, encoding="utf-8")
        print(f"✓ Scaffolded {args.framework} prompt at {out_file}")
        return 0
```
4. Add handler for `lint`:
```python
    if args.command == "lint":
        text = _read_file_or_str(args.target)
        profile_file = repos_dir / args.repo / "profile.yaml"
        profile = None
        if profile_file.exists():
            from prompt_eng.models import load_yaml_simple, RepoProfile, StackInfo
            loaded = load_yaml_simple(profile_file.read_text(encoding="utf-8"))
            st = loaded.get("stack", {})
            profile = RepoProfile(
                name=loaded.get("name", args.repo),
                path=loaded.get("path", ""),
                description=loaded.get("description", ""),
                stack=StackInfo(
                    language=st.get("language", ""),
                    package_manager=st.get("package_manager", ""),
                    test_framework=st.get("test_framework", ""),
                    linter=st.get("linter", ""),
                ),
                invariants=loaded.get("invariants", []),
                failure_gates=loaded.get("failure_gates", []),
            )

        report = lint_prompt(text, profile, framework=args.framework, prompt_name=args.target)
        if not report.issues:
            print(f"✓ Lint passed: No issues found for '{args.target}'")
            return 0

        print(f"\n--- Lint Report: {args.target} ({report.repo}) ---")
        for issue in report.issues:
            color = "\033[31m" if issue.severity == "ERROR" else "\033[33m"
            print(f"{color}[{issue.severity}]\033[0m {issue.rule_id}: {issue.message}")
            if issue.suggestion:
                print(f"  ↳ Suggestion: {issue.suggestion}")
        print("--------------------------------------------------\n")

        if report.has_errors or (report.has_warnings and args.strict):
            return 1
        return 0
```
5. Update `search` handler to pass structured filters and support `--json`:
```python
    if args.command == "search":
        matches = query_prompt_catalog(
            repos_dir,
            args.query,
            repo=args.repo,
            framework=args.framework,
            min_score=args.min_score,
        )
        if args.json:
            import json
            print(json.dumps(matches, indent=2))
            return 0

        print(f"Found {len(matches)} prompt(s) matching query:\n")
        for m in matches:
            print(f"[{m['repo']}] {m['file']} (FW: {m['framework']}, Score: {m['overall_score']})")
            print(f"  {m['preview']}\n")
        return 0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_cli.py -v`  
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add prompt_eng/cli.py tests/test_cli.py
git commit -m "feat(cli): wire up scaffold, lint, and filtered search subcommands"
```

---

### Task 7: Open Source Repository Hardening, Hygiene, & Documentation

**Files:**
- Create: `LICENSE`
- Modify: `.gitignore`
- Create: `repos/.gitkeep`
- Create: `repos/example-repo/profile.yaml`
- Modify: `README.md`

**Responsibilities:**
- Add MIT License (2026, 0xrizz)
- Untrack and gitignore local repository outputs `repos/*` (except `repos/.gitkeep` and `repos/example-repo/`)
- Update `README.md` with badges, new commands documentation (`scaffold`, `lint`, and `--json`), and open source contribution guidelines

- [ ] **Step 1: Create `LICENSE` file**

Create `LICENSE`:

```text
MIT License

Copyright (c) 2026 0xrizz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 2: Update `.gitignore` and create `repos/example-repo/profile.yaml`**

Update `.gitignore`: Add:
```gitignore
# Local multi-repo prompt profiles (keep example-repo and .gitkeep)
repos/*
!repos/.gitkeep
!repos/example-repo/
```
Create `repos/.gitkeep` and `repos/example-repo/profile.yaml`:
```yaml
name: example-repo
path: /path/to/example-repo
description: Example service for Prompt Studio demonstration
stack:
  language: Python
  package_manager: uv
  test_framework: pytest
  linter: ruff
harness:
  instruction_files:
    - AGENTS.md
  active_skills:
    - prompt-architect
  rules: []
invariants:
  - "Fast offline unit tests: uv run pytest tests/"
  - "Zero external runtime dependencies"
last_scanned: "2026-10-15T12:00:00+00:00"
```
Untrack local repos in git index:
```bash
git rm -r --cached repos/
git add repos/.gitkeep repos/example-repo/profile.yaml .gitignore LICENSE
```

- [ ] **Step 3: Update `README.md` with complete documentation & badges**

Update `README.md` to document all CLI commands including `prompt-eng scaffold`, `prompt-eng lint`, `prompt-eng search --json`, architecture, and open source license badge.

- [ ] **Step 4: Run full test suite and linters to verify everything is clean**

Run:
```bash
uv run pytest tests/ -v
uv run ruff check .
uv run ruff format --check .
```
Expected: 100% tests pass (<2.5s), zero ruff errors or formatting issues.

- [ ] **Step 5: Commit**

```bash
git add README.md LICENSE .gitignore repos/
git commit -m "chore(release): configure MIT license, privacy gitignore, and open-source documentation"
```

---

### Task 8: Create GitHub Remote & Push to `0xrizz/prompt-engineer`

**Prerequisites:**
- GitHub CLI authenticated (`gh auth status`)
- Working tree clean

- [ ] **Step 1: Check git status**

Run: `git status`  
Expected: Clean working tree, nothing to commit.

- [ ] **Step 2: Create public GitHub repository via `gh` CLI**

Run:
```bash
gh repo create 0xrizz/prompt-engineer --public --source=. --remote=origin --description "Centralized Prompt Engineering Studio & Multi-Repo Hub for Agentic Codebases"
```

- [ ] **Step 3: Push master branch to origin**

Run:
```bash
git push -u origin master
```
Expected: Branch `master` set up to track `origin/master`, all commits pushed successfully.

- [ ] **Step 4: Verify remote repo status**

Run:
```bash
gh repo view 0xrizz/prompt-engineer --web=false
```
Expected: Displays public repository details on github.com/0xrizz/prompt-engineer.

---

## Self-Review Checklist

- [x] **Spec coverage:** All 4 components from the design spec (Scaffolder, Linter, Transcript Normalizer, Filtered Search) plus Open Source Release are covered with discrete tasks.
- [x] **Placeholder scan:** Zero instances of "TODO", "TBD", or unmanifested placeholders. All code blocks and markdown files are explicitly written out.
- [x] **Zero-stall invariant:** All commands run non-interactively; no blocking stdin prompts.
- [x] **Python 3.14 Standard Library:** No third-party dependencies added to `pyproject.toml`.
