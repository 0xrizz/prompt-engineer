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
        if profile
        and profile.stack
        and profile.stack.package_manager
        and profile.stack.test_framework
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
        invariants_text = (
            "- Strictly follow repository coding conventions and test-first discipline."
        )

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
