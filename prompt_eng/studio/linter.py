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
    strict: bool = False,
) -> LintReport:
    """Evaluate prompt against repository invariants, framework structure, and rubric thresholds."""
    if isinstance(prompt_name, bool):
        strict = prompt_name
        prompt_name = "prompt"

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
        if "python" in lang and re.search(r"\b(npm|yarn|pnpm|bun)\b", text, re.IGNORECASE):
            issues.append(
                LintIssue(
                    severity="ERROR",
                    rule_id="ERR-TOOLCHAIN-MISMATCH",
                    message=f"Prompt references Node package managers in a Python project (`{profile.name}`)",
                    suggestion="Replace references with uv/python/pytest.",
                )
            )
        elif any(js_lang in lang for js_lang in ["node", "javascript", "typescript"]) and re.search(
            r"\b(pip|pytest|uv run)\b", text, re.IGNORECASE
        ):
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
        w
        for w in ["thing", "stuff", "maybe", "something", "etc"]
        if re.search(rf"\b{w}\b", text, re.IGNORECASE)
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
    if strict and any(i.severity == "WARNING" for i in issues):
        is_valid = False

    return LintReport(
        repo=profile.name if profile else "unknown",
        prompt_name=prompt_name,
        is_valid=is_valid,
        issues=issues,
    )
