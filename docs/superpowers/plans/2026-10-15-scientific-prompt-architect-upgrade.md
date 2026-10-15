# Scientific Prompt Architect Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade `prompt-engineer` and `prompt-architect` to version 4.0.0, expanding the framework catalog from 31 to 35 SOTA frameworks (GoT, Meta-Prompting, BoT, Medprompt), adding a 6th rubric dimension for Attention & Cognitive Dynamics, embedding web architecture invariants, and upgrading the Python scaffolder and linter engines.

**Architecture:** Python standard library 3.14 dataclasses and regex utilities are extended in `prompt_eng/models.py`, `scorer.py`, `scaffolder.py`, and `linter.py` to support 6-dimension evaluation and 35 frameworks. The skill files in `.agents/skills/prompt-architect/SKILL.md` and `.claude/skills/prompt-architect/SKILL.md` are upgraded and synchronized as the single source of truth for agentic prompting.

**Tech Stack:** Python 3.14 (standard library only), `pytest`, `ruff`, Markdown, GitHub CLI.

**Spec:** [docs/superpowers/specs/2026-10-15-scientific-prompt-architect-upgrade-design.md](file:///home/rizz/dev/prompt-engineer/docs/superpowers/specs/2026-10-15-scientific-prompt-architect-upgrade-design.md)

## Global Constraints

- Zero external runtime dependencies in `pyproject.toml` (`dependencies = []`).
- 100% tests pass offline via `uv run pytest tests/` in $< 2.5$ seconds.
- Linter clean via `uv run ruff check .` and `uv run ruff format --check .`.
- Skill shadowing: `.agents/skills/prompt-architect/SKILL.md` and `.claude/skills/prompt-architect/SKILL.md` must remain 100% identical.
- Author attribution remains `0xrizz`, version bumps to `4.0.0`.
- Repo isolation: no mutations outside `/home/rizz/dev/prompt-engineer`.

---

### Task 1: Extend Data Models & Rubric Scorer with Cognitive Attention Dimension

**Files:**
- Modify: `prompt_eng/models.py:53-74`
- Modify: `prompt_eng/studio/scorer.py:10-95`
- Test: `tests/test_models.py`
- Test: `tests/test_studio.py`

**Interfaces:**
- Consumes: `RubricScore` in `prompt_eng/models.py`
- Produces: `RubricScore.cognitive: float | None`, `evaluate_rubric(prompt_text: str) -> RubricScore` computing 6 dimensions when cognitive features are evaluated.

- [ ] **Step 1: Write failing unit tests for 6-dimension RubricScore and cognitive evaluation**

In `tests/test_models.py`, add test method to `TestModels`:
```python
    def test_rubric_score_cognitive_dimension(self):
        score = RubricScore(
            clarity=8.0,
            specificity=8.0,
            context=8.0,
            completeness=8.0,
            structure=8.0,
            cognitive=8.0,
        )
        self.assertEqual(score.cognitive, 8.0)
        self.assertEqual(score.overall, 8.0)
```

In `tests/test_studio.py`, add test method to `TestStudio`:
```python
    def test_evaluate_rubric_cognitive_scoring(self):
        # A prompt with sandwich architecture (Head anchor and Tail anchor)
        sandwich_prompt = """## Role
You are an expert engineer.

## Context
Background context here.

## Expectation
Return valid JSON.
"""
        score = evaluate_rubric(sandwich_prompt)
        self.assertIsNotNone(score.cognitive)
        self.assertGreaterEqual(score.cognitive, 7.0)

        # A prompt with naive negation clusters
        negative_prompt = (
            "Do not use foo. Never call bar. Don't touch baz. Cannot do qux."
        )
        neg_score = evaluate_rubric(negative_prompt)
        self.assertIsNotNone(neg_score.cognitive)
        self.assertLess(neg_score.cognitive, 7.0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_models.py -k test_rubric_score_cognitive_dimension -v`
Expected: FAIL (`TypeError: RubricScore.__init__() got an unexpected keyword argument 'cognitive'`)

- [ ] **Step 3: Implement cognitive dimension in `models.py` and `scorer.py`**

In `prompt_eng/models.py`:
```python
@dataclass
class RubricScore:
  clarity: float
  specificity: float
  context: float
  completeness: float
  structure: float
  cognitive: float | None = None
  overall: float | None = None

  def __post_init__(self) -> None:
    if self.overall is None:
      if self.cognitive is not None:
        self.overall = round(
            (
                self.clarity
                + self.specificity
                + self.context
                + self.completeness
                + self.structure
                + self.cognitive
            )
            / 6.0,
            1,
        )
      else:
        self.overall = round(
            (
                self.clarity
                + self.specificity
                + self.context
                + self.completeness
                + self.structure
            )
            / 5.0,
            1,
        )
```

In `prompt_eng/studio/scorer.py`:
Update `evaluate_rubric` to evaluate cognitive dynamics:
```python
    # Cognitive / Attention scoring
    cognitive = 6.0
    # Reward sandwich architecture (Head anchor + Tail anchor)
    has_head_anchor = bool(
        re.search(
            r"^(##\s*(role|system|context|objective)|you are)",
            text,
            re.IGNORECASE | re.MULTILINE,
        )
    )
    has_tail_anchor = bool(
        re.search(
            r"(##\s*(expectation|output|response|verify|steps|narrowing)|return|must return)",
            text,
            re.IGNORECASE,
        )
    )
    if has_head_anchor and has_tail_anchor:
      cognitive += 2.0

    # Penalize naive negation clusters ("do not", "never", "don't", "cannot")
    negation_matches = len(
        re.findall(r"\b(do not|never|don't|cannot)\b", text, re.IGNORECASE)
    )
    if negation_matches >= 3:
      cognitive -= 2.0
    elif negation_matches >= 1:
      cognitive -= 0.5

    def _clamp(v: float) -> float:
      return max(1.0, min(10.0, round(v, 1)))

    return RubricScore(
        clarity=_clamp(clarity),
        specificity=_clamp(specificity),
        context=_clamp(context),
        completeness=_clamp(completeness),
        structure=_clamp(structure),
        cognitive=_clamp(cognitive),
    )
```

Update `render_rubric_table` to include `Cognitive Dynamics`:
```python
def render_rubric_table(score: RubricScore) -> str:
  """Render a markdown table representation of rubric evaluation scores."""
  lines = [
      "| Dimension          | Score (1-10) | Evaluation Band |",
      "|--------------------|--------------|-----------------|",
      (
          f"| Clarity            | {score.clarity:<12} |"
          f" {'Solid' if score.clarity >= 7 else 'Underspecified'} |"
      ),
      (
          f"| Specificity        | {score.specificity:<12} |"
          f" {'Solid' if score.specificity >= 7 else 'Underspecified'} |"
      ),
      (
          f"| Context            | {score.context:<12} |"
          f" {'Solid' if score.context >= 7 else 'Underspecified'} |"
      ),
      (
          f"| Completeness       | {score.completeness:<12} |"
          f" {'Solid' if score.completeness >= 7 else 'Underspecified'} |"
      ),
      (
          f"| Structure          | {score.structure:<12} |"
          f" {'Solid' if score.structure >= 7 else 'Underspecified'} |"
      ),
  ]
  if score.cognitive is not None:
    lines.append(
        f"| Cognitive Dynamics | {score.cognitive:<12} |"
        f" {'Solid' if score.cognitive >= 7 else 'Underspecified'} |"
    )
  lines.extend([
      "|--------------------|--------------|-----------------|",
      (
          f"| **Overall**        | **{score.overall}**      |"
          f" {'Production Ready' if score.overall is not None and score.overall >= 8 else 'Needs Framework'} |"
      ),
  ])
  return "\n".join(lines)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_models.py tests/test_studio.py -v`
Expected: PASS (all tests pass)

- [ ] **Step 5: Commit changes**

```bash
git add prompt_eng/models.py prompt_eng/studio/scorer.py tests/test_models.py tests/test_studio.py
git commit -m "feat(scorer): add cognitive dynamics dimension to rubric scoring and models"
```

---

### Task 2: Implement Scaffolding for SOTA Reasoning Frameworks & Web Contracts

**Files:**
- Modify: `prompt_eng/studio/scaffolder.py`
- Test: `tests/test_scaffolder.py`

**Interfaces:**
- Consumes: `RepoProfile`, `evaluate_rubric`
- Produces: `scaffold_prompt` supporting `GOT`, `META-PROMPTING`, `BOT`, `MEDPROMPT`, `WEB-ACCESSIBLE`, `DEFENSIVE-ACTION`.

- [ ] **Step 1: Write failing unit tests for new framework scaffolding**

In `tests/test_scaffolder.py`:
```python
    def test_scaffold_got_framework(self):
        meta, body = scaffold_prompt(
            self.profile, "test-repo", "dag-planner", "GOT"
        )
        self.assertEqual(meta["framework"], "GOT")
        self.assertIn("## Graph Topology (DAG)", body)
        self.assertIn("## Generation Nodes", body)
        self.assertIn("## Aggregation & Scoring", body)
        self.assertIn("## Refinement & Exit Criteria", body)

    def test_scaffold_meta_prompting_framework(self):
        meta, body = scaffold_prompt(
            self.profile, "test-repo", "conductor-orchestration", "META-PROMPTING"
        )
        self.assertEqual(meta["framework"], "META-PROMPTING")
        self.assertIn("## Conductor System Instructions", body)
        self.assertIn("## Specialist Agent Personas", body)
        self.assertIn("## Isolated Delegation Protocol", body)

    def test_scaffold_bot_framework(self):
        meta, body = scaffold_prompt(
            self.profile, "test-repo", "thought-buffer", "BOT"
        )
        self.assertEqual(meta["framework"], "BOT")
        self.assertIn("## Distilled Meta-Buffer Templates", body)
        self.assertIn("## Problem Distillation", body)

    def test_scaffold_medprompt_framework(self):
        meta, body = scaffold_prompt(
            self.profile, "test-repo", "clinical-eval", "MEDPROMPT"
        )
        self.assertEqual(meta["framework"], "MEDPROMPT")
        self.assertIn("## Dynamic Few-Shot Exemplars", body)
        self.assertIn("## Choice-Shuffle Ensembling", body)

    def test_scaffold_web_contracts(self):
        meta_web, body_web = scaffold_prompt(
            self.profile, "test-repo", "accessible-card", "WEB-ACCESSIBLE"
        )
        self.assertEqual(meta_web["framework"], "WEB-ACCESSIBLE")
        self.assertIn("## Semantic Landmark Hierarchy", body_web)
        self.assertIn("## Keyboard & ARIA State Contracts", body_web)

        meta_sec, body_sec = scaffold_prompt(
            self.profile, "test-repo", "secure-action", "DEFENSIVE-ACTION"
        )
        self.assertEqual(meta_sec["framework"], "DEFENSIVE-ACTION")
        self.assertIn("## Boundary Contract (Server Action)", body_sec)
        self.assertIn("## Runtime Schema (Zod)", body_sec)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_scaffolder.py -k test_scaffold_got_framework -v`
Expected: FAIL (falls back to fallback branch)

- [ ] **Step 3: Implement new framework branches in `scaffolder.py`**

In `prompt_eng/studio/scaffolder.py`, add branches for:
- `fw in ("GOT", "GRAPH-OF-THOUGHTS")`
- `fw in ("META-PROMPTING", "METAPROMPTING")`
- `fw in ("BOT", "BUFFER-OF-THOUGHTS")`
- `fw == "MEDPROMPT"`
- `fw in ("WEB-ACCESSIBLE", "WEB_ACCESSIBLE")`
- `fw in ("DEFENSIVE-ACTION", "DEFENSIVE_ACTION")`
Ensure frontmatter includes `cognitive` score in `meta["score"]`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_scaffolder.py -v`
Expected: PASS (all tests pass)

- [ ] **Step 5: Commit changes**

```bash
git add prompt_eng/studio/scaffolder.py tests/test_scaffolder.py
git commit -m "feat(scaffolder): add templates for GoT, Meta-Prompting, BoT, Medprompt, and Web contracts"
```

---

### Task 3: Implement Cognitive & Boundary Rules in Prompt Linter

**Files:**
- Modify: `prompt_eng/studio/linter.py`
- Test: `tests/test_linter.py`

**Interfaces:**
- Consumes: `LintIssue`, `LintReport`, `RepoProfile`, `evaluate_rubric`
- Produces: `lint_prompt` checking framework completeness for new frameworks, `WARN-SANDWICH-STRUCTURE`, `WARN-NAIVE-NEGATION`, and `WARN-CLIENT-SECRET-LEAK`.

- [ ] **Step 1: Write failing unit tests for new linter checks**

In `tests/test_linter.py`:
```python
    def test_lint_detects_got_and_meta_prompting_incomplete(self):
        bad_got = "## Objective\nSolve problem."
        report = lint_prompt(bad_got, framework="GOT")
        self.assertFalse(report.is_valid)
        self.assertTrue(
            any(
                i.rule_id == "ERR-FRAMEWORK-INCOMPLETE" and "Graph Topology" in i.message
                for i in report.issues
            )
        )

    def test_lint_detects_naive_negation_warning(self):
        neg_prompt = """## Role
You are an assistant.
## Steps
Do not use var. Never use any. Don't mutate state. Cannot import lodash.
## Output
Return code.
"""
        report = lint_prompt(neg_prompt, strict=False)
        self.assertTrue(report.is_valid)  # Warning only by default
        self.assertTrue(any(i.rule_id == "WARN-NAIVE-NEGATION" for i in report.issues))

        strict_report = lint_prompt(neg_prompt, strict=True)
        self.assertFalse(strict_report.is_valid)  # Strict mode fails on warnings

    def test_lint_detects_sandwich_structure_warning(self):
        # A long prompt (>150 words) that lacks head or tail anchors
        middle_heavy = (
            "Here is a task. "
            + "We have many instructions in the middle. " * 30
            + "Just do it."
        )
        report = lint_prompt(middle_heavy)
        self.assertTrue(any(i.rule_id == "WARN-SANDWICH-STRUCTURE" for i in report.issues))

    def test_lint_detects_client_secret_leak_warning(self):
        leak_prompt = """## Component
'use client'
import React from 'react';
const secret = process.env.STRIPE_SECRET_KEY;
"""
        report = lint_prompt(leak_prompt)
        self.assertTrue(any(i.rule_id == "WARN-CLIENT-SECRET-LEAK" for i in report.issues))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_linter.py -k test_lint_detects_got_and_meta_prompting_incomplete -v`
Expected: FAIL

- [ ] **Step 3: Implement new linter rules in `linter.py`**

In `prompt_eng/studio/linter.py`:
1. Completeness checks for `GOT` (`Objective`, `Graph Topology`, `Generation Nodes`, `Aggregation & Scoring`, `Refinement & Exit Criteria`), `META-PROMPTING` (`Objective`, `Conductor System Instructions`, `Specialist Agent Personas`), `BOT` (`Objective`, `Distilled Meta-Buffer`), `MEDPROMPT` (`Objective`, `Dynamic Few-Shot Exemplars`, `Choice-Shuffle Ensembling`).
2. `WARN-SANDWICH-STRUCTURE`: Check `words > 150` and absence of head/tail anchors.
3. `WARN-NAIVE-NEGATION`: Check `len(re.findall(r"\b(do not|never|don't|cannot)\b", text, re.IGNORECASE)) >= 3` and ratio of positive bounding keywords.
4. `WARN-CLIENT-SECRET-LEAK`: Check `'use client'` alongside `process.env.SECRET` or `DATABASE_URL`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_linter.py -v`
Expected: PASS (all tests pass)

- [ ] **Step 5: Commit changes**

```bash
git add prompt_eng/studio/linter.py tests/test_linter.py
git commit -m "feat(linter): add completeness checks for GoT/Meta-Prompting, sandwich warning, and secret leak checks"
```

---

### Task 4: Connect New Frameworks to CLI Router

**Files:**
- Modify: `prompt_eng/cli.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: `scaffold_prompt`, `lint_prompt`
- Produces: CLI options `--framework` supporting `got`, `meta-prompting`, `bot`, `medprompt`, `web-accessible`, `defensive-action`.

- [ ] **Step 1: Write failing CLI integration test**

In `tests/test_cli.py`:
```python
    def test_cli_scaffold_got_framework(self):
        output = self.run_cli(
            ["scaffold", "--framework", "got", "--repo", "test-repo", "--name", "dag-task"]
        )
        self.assertIn("framework: GOT", output)
        self.assertIn("## Graph Topology (DAG)", output)

    def test_cli_scaffold_web_accessible(self):
        output = self.run_cli(
            ["scaffold", "--framework", "web-accessible", "--repo", "test-repo", "--name", "nav-bar"]
        )
        self.assertIn("framework: WEB-ACCESSIBLE", output)
        self.assertIn("## Semantic Landmark Hierarchy", output)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py -k test_cli_scaffold_got_framework -v`
Expected: FAIL (argument --framework: invalid choice)

- [ ] **Step 3: Update `cli.py` choices and descriptions**

In `prompt_eng/cli.py`:
Update `scaffold_parser.add_argument("--framework", "-f", ...)` choices to include:
`"risen"`, `"costar"`, `"co-star"`, `"bab"`, `"react"`, `"got"`, `"meta-prompting"`, `"bot"`, `"medprompt"`, `"web-accessible"`, `"defensive-action"`.
Update help string to mention SOTA reasoning and web contracts.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_cli.py -v`
Expected: PASS (all tests pass)

- [ ] **Step 5: Commit changes**

```bash
git add prompt_eng/cli.py tests/test_cli.py
git commit -m "feat(cli): wire new reasoning and web frameworks to scaffold and lint CLI"
```

---

### Task 5: Upgrade Skill Definitions to Version 4.0.0 (35 Frameworks, Cognitive Rubric, Web Guide)

**Files:**
- Modify: `.agents/skills/prompt-architect/SKILL.md`
- Modify: `.claude/skills/prompt-architect/SKILL.md`
- Test: `tests/test_skills_setup.py`

**Interfaces:**
- Consumes: `docs/research/2026-10-15-scientific-prompt-engineering-dossier.md`
- Produces: Synchronized skill files in `.agents/` and `.claude/` with version `4.0.0`, 35 frameworks catalog, 6-dimension rubric, and web codebase guide.

- [ ] **Step 1: Write failing test in `tests/test_skills_setup.py`**

In `tests/test_skills_setup.py`:
Update assertions:
```python
    def test_local_skill_shadowing_files(self):
        # ...
        self.assertIn('version: "4.0.0"', content)
        self.assertIn("35 frameworks across 7 intent categories", content)
        self.assertIn("Graph-of-Thoughts", content)
        self.assertIn("Meta-Prompting", content)
        self.assertIn("Buffer-of-Thoughts", content)
        self.assertIn("Medprompt", content)
        self.assertIn("Attention & Cognitive Dynamics", content)
        self.assertIn("WCAG 2.2", content)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_skills_setup.py -v`
Expected: FAIL (assertion error on version 4.0.0 or 35 frameworks)

- [ ] **Step 3: Update `.agents/skills/prompt-architect/SKILL.md` and `.claude/skills/prompt-architect/SKILL.md`**

1. Update frontmatter:
   ```yaml
   metadata:
     author: 0xrizz
     version: "4.0.0"
     homepage: https://github.com/0xrizz/prompt-engineer
   ```
2. Update description: `"Use when analyzing and improving prompts using 35 frameworks across 7 intent categories..."`
3. Add **Graph-of-Thoughts (GoT)** under CREATE and REASON.
4. Add **Meta-Prompting** under AGENTIC and REASON.
5. Add **Buffer-of-Thoughts (BoT)** under TRANSFORM and REASON.
6. Add **Medprompt / Dynamic Few-Shot Ensembling** under REASON and CLARIFY.
7. Add 6th dimension to rubric: **Attention & Cognitive Dynamics** (Sandwich architecture 10-80-10 & contrastive positive steering).
8. Add **Web Codebase Prompt Engineering Guide** section (3-stage pipeline, TypeScript interface stubs, Server vs Client execution boundaries, WCAG 2.2 AA / ARIA 1.2 rules, OWASP LLM Top 10 defense-in-depth).
9. Copy `.agents/skills/prompt-architect/SKILL.md` verbatim to `.claude/skills/prompt-architect/SKILL.md`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_skills_setup.py -v`
Expected: PASS

- [ ] **Step 5: Commit changes**

```bash
git add .agents/skills/prompt-architect/SKILL.md .claude/skills/prompt-architect/SKILL.md tests/test_skills_setup.py
git commit -m "feat(skills): upgrade prompt-architect to v4.0.0 with 35 frameworks, cognitive rubric, and web guide"
```

---

### Task 6: Full Offline Test Suite & Documentation Polish

**Files:**
- Modify: `README.md`
- Test: All tests in `tests/`

**Interfaces:**
- Consumes: All completed modules
- Produces: Updated documentation, 100% test pass rate, clean ruff linter.

- [ ] **Step 1: Update README.md with v4.0.0 features**

In `README.md`:
- Document 35 frameworks support.
- Document new scaffolding options (`got`, `meta-prompting`, `bot`, `medprompt`, `web-accessible`, `defensive-action`).
- Document cognitive rubric and linter rules (`WARN-SANDWICH-STRUCTURE`, `WARN-NAIVE-NEGATION`, `WARN-CLIENT-SECRET-LEAK`).

- [ ] **Step 2: Run full test suite and formatters**

```bash
uv run pytest tests/ -v
uv run ruff check .
uv run ruff format --check .
```
Expected: All tests pass ($> 85$ tests), 0 linter errors, clean formatting.

- [ ] **Step 3: Commit changes**

```bash
git add README.md
git commit -m "docs: document v4.0.0 scientific prompting features, 35 frameworks, and cognitive linter"
```

---

### Task 7: Push Master Branch to Remote GitHub

**Files:**
- Remote: `https://github.com/0xrizz/prompt-engineer`

**Responsibilities:**
- Push local `master` branch to GitHub `origin/master`.
- Verify GitHub status.

- [ ] **Step 1: Verify git status is clean**

Run: `git status`
Expected: `nothing to commit, working tree clean`

- [ ] **Step 2: Push commits to GitHub**

Run: `git push origin master`
Expected: Successfully pushed to `origin/master`.

- [ ] **Step 3: Verify remote status**

Run: `gh repo view 0xrizz/prompt-engineer --web=false`
Expected: Displays repo information cleanly.
