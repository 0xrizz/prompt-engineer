# Final Review Fix Report: Central Prompt Engineering Studio & Hub

- **Date**: 2026-09-22
- **Status**: COMPLETE
- **Test Suite**: 50/50 tests passing (`uv run pytest tests/` and `python3 -m unittest discover -s tests`)
- **Linter & Formatter**: 100% compliant (`uv run ruff format .` and `uv run ruff check .`)

---

## Executive Summary

All 6 findings identified during the final whole-branch review of Central Prompt Engineering Studio & Hub have been resolved and verified with dedicated test coverage. The working tree remains 100% clean when running tests, and all target repository profiles have been regenerated with improved manifests and deduplicated invariants.

---

## Detailed Findings and Resolutions

### 1. Critical: Silent Fallback in `resolver.py` & Test Fixture Path in `test_cli.py`
- **Issue**: `SessionResolver.resolve_session` silently fell back to `find_latest_session` even when `file_path` did not exist or when an explicit `session_id` was specified and not found. In `tests/test_cli.py:110`, a reference to non-existent `antigravity_session.jsonl` was masking this bug.
- **Resolution**:
  - In `prompt_eng/transcripts/resolver.py`: Added explicit checks to raise `FileNotFoundError` if `file_path` is passed and does not exist, or if `session_id` is passed and cannot be found in either Antigravity brain or Claude projects.
  - In `tests/test_cli.py`: Updated fixture path to `tests/fixtures/antigravity_sample.jsonl`.
  - Added unit tests in `tests/test_transcripts.py` verifying that missing file paths and non-existent session IDs explicitly raise `FileNotFoundError`.

### 2. Important: YAML String List Items Quoting in `models.py`
- **Issue**: When serializing list items containing colons (e.g. `- **Rule**: Detail`), simple YAML serializers and parsers misinterpreted string items as dictionaries or failed on special YAML syntax characters.
- **Resolution**:
  - In `dump_yaml_simple`: When a string list item contains `: `, ends with `:`, or begins with special YAML control characters (`-`, `#`, `@`, `!`, `*`, `&`, `|`, `>`, `%`, `?`, `[`, `{`, `"`, `'`), wrapped the item in double quotes with internal quotes escaped.
  - In `_parse_scalar` and `load_yaml_simple`: Stripped double quotes and treated quoted items as scalar strings rather than parsing key-value pairs.
  - In `tests/test_models.py`: Added `test_yaml_list_item_with_colon_quoted` verifying round-trip integrity for strings containing `: `.

### 3. Important: Prevent Tests from Mutating Tracked Working Tree in `test_e2e.py`
- **Issue**: `test_e2e_scan_and_profile_flow` previously invoked `prompt-eng scan --root /home/rizz/dev`, writing updated profiles directly into the tracked `repos/` folder, causing dirty timestamps in `git status`.
- **Resolution**:
  - In `prompt_eng/cli.py`: Added `--output` argument to `prompt-eng scan` (defaulting to `repos/`), enabling callers to specify custom output destinations.
  - In `tests/test_e2e.py`: Refactored `test_e2e_scan_and_profile_flow` to execute scans into an isolated `tempfile.TemporaryDirectory()`.
  - Verified running `uv run pytest tests/` leaves `git status` 100% clean and does not mutate tracked repository profiles.

### 4. Important: Deduplicate Invariants & Improve Detection in `scanner.py`
- **Issue**: Duplicate invariant strings were collected across multiple instruction files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`). Projects without `pyproject.toml` (e.g. using `requirements.txt` or `setup.py`) or projects with `uv.lock` were not optimally classified. Descriptions from manifests were not populated.
- **Resolution**:
  - In `prompt_eng/scanner.py`:
    - Added invariant deduplication preserving original sequence.
    - Added `uv.lock` detection setting `stack.package_manager = "uv"`.
    - Added fallback Python detection via `requirements.txt` / `setup.py` / `uv.lock`.
    - Added extraction of `description` from `pyproject.toml` and `package.json` to populate `profile.description`.
  - Added test cases in `tests/test_scanner.py`: `test_deduplicate_invariants`, `test_scan_uv_lock_detection`, `test_scan_requirements_and_setup_py`, and `test_description_extraction`.

### 5. Important: Clean Up Tool Counting in `claude.py`
- **Issue**: `parse_claude_transcript` double-counted tools by checking `if "tool_use" in str(entry)` and falsely added tool invocations whenever the word "command" appeared in transcript text.
- **Resolution**:
  - In `prompt_eng/transcripts/claude.py`: Removed loose substring checks (`"command"` and `str(entry)`). Strictly appended tool names from structured `tool_use` blocks.
  - In `tests/test_transcripts.py`: Added `test_claude_tool_counting_exact` verifying exact tool counts without false positives.

### 6. Minor: Add `--format [md|json]` to `transcript` command & Ruff Format
- **Issue**: `transcript` command only supported markdown output; formatting across the codebase needed verification.
- **Resolution**:
  - In `prompt_eng/cli.py`: Added `--format` argument to `transcript` subparser (`choices=["md", "json"]`, default="md"). In `json` mode, outputs formatted JSON via `dataclasses.asdict(summary)`.
  - Re-scanned `/home/rizz/dev` to refresh `repos/*/profile.yaml` with deduplicated invariants, descriptions, and proper YAML quoting.
  - Added `test_transcript_command_json_format` to `tests/test_cli.py`.
  - Ran `uv run ruff format .` and `uv run ruff check .` across the workspace with zero lint errors.
  - Ran full test suites: 50 unit and integration tests passing.
