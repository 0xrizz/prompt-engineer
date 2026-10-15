"""5-dimension rubric scoring engine based on prompt-architect guidelines."""

from __future__ import annotations

import re

from prompt_eng.models import RubricScore


def evaluate_rubric(prompt_text: str) -> RubricScore:
    """Evaluate a prompt across 5 dimensions: clarity, specificity, context, completeness, and structure."""
    text = prompt_text.strip()
    words = len(text.split())

    # Clarity scoring
    vague_words = ["thing", "stuff", "something", "maybe", "etc"]
    clarity = 8.0
    for w in vague_words:
        if re.search(rf"\b{w}\b", text, re.IGNORECASE):
            clarity -= 1.5
    if words < 5:
        clarity -= 3.0

    # Specificity scoring
    specificity = 5.0
    if any(
        q in text.lower() for q in ["return", "format", "must", "only", "json", "markdown", "table"]
    ):
        specificity += 2.0
    if re.search(r"\b\d+\b", text):
        specificity += 1.0

    # Context scoring
    context = 4.0
    if any(
        c in text.lower()
        for c in ["because", "in order to", "repo", "using", "framework", "version"]
    ):
        context += 3.0

    # Completeness scoring
    completeness = 5.0
    if any(
        k in text.lower()
        for k in [
            "role:",
            "task:",
            "context:",
            "goal:",
            "steps:",
            "## role",
            "## task",
            "## context",
            "## goal",
            "## steps",
        ]
    ):
        completeness += 3.0
    elif words > 20:
        completeness += 1.5

    # Structure scoring
    structure = 5.0
    if "\n" in text:
        structure += 2.0
    if any(line.strip().startswith(("-", "*", "1.")) for line in text.splitlines()):
        structure += 2.0

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
    negation_matches = len(re.findall(r"\b(do not|never|don't|cannot)\b", text, re.IGNORECASE))
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
    lines.extend(
        [
            "|--------------------|--------------|-----------------|",
            (
                f"| **Overall**        | **{score.overall}**      |"
                f" {'Production Ready' if score.overall is not None and score.overall >= 8 else 'Needs Framework'} |"
            ),
        ]
    )
    return "\n".join(lines)
