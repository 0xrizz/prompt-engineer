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
    elif fw in ("GOT", "GRAPH-OF-THOUGHTS"):
        required = [
            "Objective",
            "Graph Topology",
            "Generation Nodes",
            "Aggregation & Scoring",
            "Refinement & Exit Criteria",
        ]
        missing = [
            sec for sec in required if not re.search(rf"##\s+{re.escape(sec)}", text, re.IGNORECASE)
        ]
        if missing:
            issues.append(
                LintIssue(
                    severity="ERROR",
                    rule_id="ERR-FRAMEWORK-INCOMPLETE",
                    message=f"GOT prompt missing required section(s): {', '.join(missing)}",
                    suggestion=f"Add ## {missing[0]} to ensure Graph-of-Thoughts compliance.",
                )
            )
    elif fw in ("META-PROMPTING", "METAPROMPTING"):
        required = [
            "Objective",
            "Conductor System Instructions",
            "Specialist Agent Personas",
        ]
        missing = [
            sec for sec in required if not re.search(rf"##\s+{re.escape(sec)}", text, re.IGNORECASE)
        ]
        if missing:
            issues.append(
                LintIssue(
                    severity="ERROR",
                    rule_id="ERR-FRAMEWORK-INCOMPLETE",
                    message=f"META-PROMPTING prompt missing required section(s): {', '.join(missing)}",
                    suggestion=f"Add ## {missing[0]} to ensure Meta-Prompting compliance.",
                )
            )
    elif fw in ("BOT", "BUFFER-OF-THOUGHTS"):
        required = [
            "Objective",
            "Distilled Meta-Buffer",
        ]
        missing = [
            sec for sec in required if not re.search(rf"##\s+{re.escape(sec)}", text, re.IGNORECASE)
        ]
        if missing:
            issues.append(
                LintIssue(
                    severity="ERROR",
                    rule_id="ERR-FRAMEWORK-INCOMPLETE",
                    message=f"BOT prompt missing required section(s): {', '.join(missing)}",
                    suggestion=f"Add ## {missing[0]} to ensure Buffer-of-Thoughts compliance.",
                )
            )
    elif fw == "MEDPROMPT":
        required = [
            "Objective",
            "Dynamic Few-Shot Exemplars",
            "Choice-Shuffle Ensembling",
        ]
        missing = [
            sec for sec in required if not re.search(rf"##\s+{re.escape(sec)}", text, re.IGNORECASE)
        ]
        if missing:
            issues.append(
                LintIssue(
                    severity="ERROR",
                    rule_id="ERR-FRAMEWORK-INCOMPLETE",
                    message=f"MEDPROMPT prompt missing required section(s): {', '.join(missing)}",
                    suggestion=f"Add ## {missing[0]} to ensure Medprompt compliance.",
                )
            )
    elif fw in ("WEB-ACCESSIBLE", "WEB_ACCESSIBLE"):
        required = [
            "Semantic Landmark Hierarchy",
            "Component Interface Stubs",
            "Keyboard & ARIA State Contracts",
        ]
        missing = [
            sec for sec in required if not re.search(rf"##\s+{re.escape(sec)}", text, re.IGNORECASE)
        ]
        if missing:
            issues.append(
                LintIssue(
                    severity="ERROR",
                    rule_id="ERR-FRAMEWORK-INCOMPLETE",
                    message=f"WEB-ACCESSIBLE prompt missing required section(s): {', '.join(missing)}",
                    suggestion=f"Add ## {missing[0]} to ensure accessibility compliance.",
                )
            )
    elif fw in ("DEFENSIVE-ACTION", "DEFENSIVE_ACTION"):
        required = [
            "Boundary Contract",
            "Runtime Schema",
            "Session Authorization",
        ]
        missing = [
            sec for sec in required if not re.search(rf"##\s+{re.escape(sec)}", text, re.IGNORECASE)
        ]
        if missing:
            issues.append(
                LintIssue(
                    severity="ERROR",
                    rule_id="ERR-FRAMEWORK-INCOMPLETE",
                    message=f"DEFENSIVE-ACTION prompt missing required section(s): {', '.join(missing)}",
                    suggestion=f"Add ## {missing[0]} to ensure defensive boundary compliance.",
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

    # 3. Cognitive Dynamics & Boundary Checks (WARNING)
    # 3a. Sandwich structure check
    words = len(text.split())
    if words > 150:
        has_head_anchor = bool(
            re.search(
                r"^(##\s*(role|system|context|objective)|you are)",
                text,
                re.IGNORECASE | re.MULTILINE,
            )
        )
        has_tail_anchor = bool(
            re.search(
                r"(##\s*(expectation|output|response|verify|verification|steps|narrowing|format|criteria)|return|must return)",
                text,
                re.IGNORECASE,
            )
        )
        if not (has_head_anchor and has_tail_anchor):
            issues.append(
                LintIssue(
                    severity="WARNING",
                    rule_id="WARN-SANDWICH-STRUCTURE",
                    message=f"Prompt length ({words} words > 150) lacks explicit sandwich structure (Head/Tail anchor)",
                    suggestion="Structure long prompts with a clear Head anchor (Role/Context/Objective) and Tail anchor (Output/Verification/Expectations) to prevent lost-in-the-middle degradation.",
                )
            )

    # 3b. Naive negation cluster check
    negation_matches = re.findall(r"\b(do not|never|don't|cannot)\b", text, re.IGNORECASE)
    positive_bounding = re.findall(
        r"\b(must|only|require|ensure|always|instead|exclusively)\b",
        text,
        re.IGNORECASE,
    )
    if len(negation_matches) >= 3 and (len(positive_bounding) / len(negation_matches) < 0.6):
        issues.append(
            LintIssue(
                severity="WARNING",
                rule_id="WARN-NAIVE-NEGATION",
                message=f"Prompt contains cluster of {len(negation_matches)} naive negative constraints without sufficient contrastive positive bounding",
                suggestion="Replace negative prohibitions ('do not', 'never') with contrastive positive steering ('use exclusively', 'must', 'ensure').",
            )
        )

    # 3c. Client secret leak check
    if re.search(r"['\"]use client['\"]", text, re.IGNORECASE) and (
        re.search(
            r"\bprocess\.env\.(?!NEXT_PUBLIC_|VITE_)\w*(SECRET|KEY|TOKEN|PASSWORD|URL)\w*",
            text,
            re.IGNORECASE,
        )
        or re.search(r"\bDATABASE_URL\b", text, re.IGNORECASE)
    ):
        issues.append(
            LintIssue(
                severity="WARNING",
                rule_id="WARN-CLIENT-SECRET-LEAK",
                message="Client component ('use client') references private environment variable or database connection token",
                suggestion="Move secret or database access to a Server Component or Server Action ('use server') to prevent client-side credential exposure.",
            )
        )

    # 4. Rubric & Vague Language Checks (WARNING)
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
