# Performance Enhancement Suite Technical Specification

- **Date:** 2026-10-15
- **Author:** Prompt Studio Architect
- **Status:** Approved
- **Target Repo:** `prompt-engineer` (`/home/rizz/dev/prompt-engineer`)
- **Governing Standard:** Antigravity / Claude Code Prompt Studio Standard (Python 3.14, Zero External Dependencies)

---

## 1. Executive Summary & Problem Context

The `prompt-engineer` hub serves as the central command studio for authoring, evaluating, and cataloging prompts across all repositories in `/home/rizz/dev/`. Empirical analysis of 32 historical prompts across 14 tracked repositories revealed critical operational bottlenecks:

1. **Ingestion & Session Discovery Flaw:** `SessionResolver.find_latest_session` sorted all sessions by global timestamp without filtering by repository workspace, resulting in cross-project context pollution. Furthermore, Antigravity JSONL logs leaked harness XML scaffolding (`<USER_SETTINGS_CHANGE>`, `<ADDITIONAL_METADATA>`) into extracted user goals.
2. **Authoring Velocity Friction:** Authors manually hand-crafted prompt structures (e.g. RISEN, CO-STAR) from scratch and manually copied repository invariants from `profile.yaml`, slowing iteration cycles.
3. **Safety & Governance Blindspot:** Although multi-repo profiling captures failure gates and repository invariants, the studio lacked a deterministic verification mechanism (`lint`) to assert that prompts do not hallucinate dependencies or violate target repo guardrails.
4. **Catalog Query Inefficiency:** As the prompt catalog grew to 32+ prompts, querying was limited to unindexed substring matching without structured filters for frameworks, minimum scores, or target repositories.

This specification details the architecture for the **Performance Enhancement Suite**: a four-module upgrade that resolves these bottlenecks while strictly preserving the repository's zero-external-dependency invariant and offline test execution speeds (<2.5s).

---

## 2. Architectural Invariants & Constraints

1. **Zero External Runtime Dependencies:** The entire studio runtime MUST rely exclusively on Python 3.14 standard library (`pathlib`, `json`, `re`, `argparse`, `dataclasses`, `difflib`, `datetime`). Zero additions to `dependencies` in `pyproject.toml`.
2. **Repo Isolation:** Mutating file operations are strictly confined to `/home/rizz/dev/prompt-engineer/`. No direct mutations to target repositories.
3. **Deterministic Fast Offline Tests:** All unit and integration tests run offline via `uv run pytest tests/` with zero network egress and execution duration < 2.5s.
4. **Backward Compatibility:** All existing CLI subcommands (`scan`, `transcript`, `profile`, `score`, `diff`, `list`, `search`, `save-prompt`) and existing profile schemas must remain fully functional.

---

## 3. Component Specifications

### 3.1 Workspace-Aware Transcript Resolver & Normalizer

#### Location:
- `prompt_eng/transcripts/resolver.py`
- `prompt_eng/transcripts/antigravity.py`

#### Responsibilities:
- **Repo-Scoped Discovery:** When `--repo <name>` is provided to `SessionResolver.find_latest_session`, resolve candidate sessions by inspecting whether the transcript's working directory (`Cwd`) or absolute file paths match `/home/rizz/dev/<name>`.
  - For Claude Code sessions (`~/.claude/projects/`), inspect directory prefixes matching `-home-rizz-dev-<name>`.
  - For Antigravity sessions (`~/.gemini/antigravity/brain/`), scan transcript events for `Cwd` or `AbsolutePath` pointing to `/home/rizz/dev/<name>`.
  - If no session matches the target repo, raise a descriptive `FileNotFoundError` rather than returning an unrelated session.
- **XML Harness Sanitization:**
  - Strip `<USER_REQUEST>` wrapper and remove `<ADDITIONAL_METADATA>` and `<USER_SETTINGS_CHANGE>` blocks to yield only the pristine user intent.
- **Robust Turn State Recovery:**
  - When scanning backwards for `last_turn_state`, skip empty `PLANNER_RESPONSE` steps (which only contain tool calls) and locate the latest substantive model thought or assistant message.

---

### 3.2 Prompt Scaffolder Engine (`prompt-eng scaffold`)

#### Location:
- `prompt_eng/studio/scaffolder.py`
- `prompt_eng/cli.py` (`scaffold` subcommand)

#### Interface Contract:
```bash
uv run prompt-eng scaffold --repo <target-repo> --name <slug> --framework <RISEN|CO-STAR|BAB|ReAct> [--intent <intent>] [--stdout]
```

#### Behavioral Specifications:
1. **Profile Grounding:** Loads `repos/<target-repo>/profile.yaml`. If not present, prompts user or falls back gracefully to default templates.
2. **Framework Synthesis:**
   - **`RISEN`**:
     - *Role*: Injected with target stack context (e.g., `Staff Systems Engineer specializing in Python 3.14 and Hatchling`).
     - *Input*: Target milestone, blueprints, or input context placeholder.
     - *Steps*: Structured step-by-step TDD sequence (Failing test -> Implementation -> Verification).
     - *Expectation*: Acceptance criteria and verification commands (e.g. `uv run pytest tests/`).
     - *Narrowing*: Directly populated with the target repo's scanned `invariants` and `failure_gates`.
   - **`CO-STAR`**:
     - *Context*: Scanned repo description, language, and active milestone.
     - *Objective*: Clear deliverable goal.
     - *Style & Tone*: Technical, authoritative, concise.
     - *Audience*: Senior engineers / AI agentic pairs.
     - *Response*: Structured Markdown deliverables conforming to repo conventions.
   - **`BAB` (Before-After-Bridge)**:
     - *Before*: Current state, limitations, or existing bugs.
     - *After*: Desired state and performance criteria.
     - *Bridge*: Concrete transition plan and code changes.
   - **`ReAct`**:
     - *Thought / Action / Observation* loop with tool invocation boundaries.
3. **Hybrid Output:**
   - If `--stdout` is set: Print generated frontmatter and body directly to standard output without disk write.
   - Default: Write to `repos/<target-repo>/prompts/<slug>.md` with initialized YAML frontmatter (`repo`, `framework`, `name`, `score`).

---

### 3.3 Prompt Invariant & Framework Linter (`prompt-eng lint`)

#### Location:
- `prompt_eng/studio/linter.py`
- `prompt_eng/cli.py` (`lint` subcommand)

#### Interface Contract:
```bash
uv run prompt-eng lint [prompt_file_or_text] --repo <target-repo> [--strict]
```

#### Validation Rules & Diagnostics:
1. **Rule 1: Invariant Conformance (Severity: ERROR)**
   - Checks prompt text against `profile.invariants` and `profile.failure_gates`.
   - Flags tool mismatch (e.g. using `npm test` or `yarn` in a Python repo whose profile specifies `pytest` and `uv`).
   - Flags prohibited behaviors (e.g. unmanifested package installations, breaking offline testing gates).
2. **Rule 2: Framework Completeness (Severity: ERROR)**
   - Verifies mandatory section components:
     - `RISEN`: Role, Input, Steps, Expectation, Narrowing/Constraints.
     - `CO-STAR`: Context, Objective, Style, Tone, Audience, Response.
     - `BAB`: Before, After, Bridge.
3. **Rule 3: Heuristic Quality & Rubric Guardrails (Severity: WARNING)**
   - Flags vague terminology (`thing`, `stuff`, `maybe`, `something`).
   - Flags prompt length < 25 words.
   - Flags rubric score < 7.0 across any dimension.
4. **Exit Codes:**
   - `0`: Success (Zero errors, warnings allowed unless `--strict` is enabled).
   - `1`: Failure (Any ERROR present, or any WARNING present with `--strict`).

---

### 3.4 Structured Catalog Search & Indexing Engine

#### Location:
- `prompt_eng/studio/catalog.py`
- `prompt_eng/cli.py` (`search` subcommand update)

#### Interface Contract:
```bash
uv run prompt-eng search [query] [--repo <repo>] [--framework <fw>] [--min-score <float>] [--json]
```

#### Behavioral Specifications:
1. **Multi-Axis Filtering:**
   - Case-insensitive substring match on prompt body and title.
   - Exact or prefix filtering on `--repo`.
   - Exact or case-insensitive match on `--framework`.
   - Numeric threshold filtering on `--min-score` against `meta.score.overall`.
2. **Formatted Output:**
   - Tabular CLI rendering showing `Repo`, `File`, `Framework`, `Score`, and snippet preview.
   - Structured JSON output when `--json` flag is provided for machine parsing and automated pipelines.

---

## 4. Data Models Updates (`prompt_eng/models.py`)

New dataclasses to support linting and structured diagnostic outputs:

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

---

## 5. Test & Verification Plan

### Test Matrix:
1. `tests/test_transcripts.py`:
   - Test repo-scoped session filtering for Antigravity and Claude Code.
   - Test XML tag stripping (`<USER_REQUEST>` vs noise tags).
   - Test fallback behavior when repo session does not exist.
2. `tests/test_scaffolder.py`:
   - Test RISEN template generation with profile invariant injection.
   - Test CO-STAR, BAB, and ReAct template generation.
   - Test `--stdout` vs filesystem write behavior.
3. `tests/test_linter.py`:
   - Test invariant violation detection (e.g. `npm` in python repo).
   - Test framework structural completeness (missing sections).
   - Test exit codes (`0` for clean/warnings, `1` for errors, `--strict` behavior).
4. `tests/test_catalog.py`:
   - Test search filtering with `--repo`, `--framework`, and `--min-score`.
   - Test JSON output formatting.
5. `tests/test_cli.py`:
   - End-to-end CLI invocations for `scaffold`, `lint`, and enhanced `search`.

### Performance Target:
- 100% test pass rate across all suites.
- Total test execution time < 2.50s.
- Zero external runtime dependencies.
