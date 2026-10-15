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
    elif fw in ("GOT", "GRAPH-OF-THOUGHTS"):
        body = f"""## Objective
Resolve `{prompt_name}` in `{repo_name}` ({lang}) using a Graph-of-Thoughts (GoT) non-linear reasoning topology.

## Graph Topology (DAG)
Model the reasoning process as a Directed Acyclic Graph $G = (V, E)$:
- Vertices ($V$): Distinct thought states (solution concepts, architectural designs, implementation slices).
- Directed Edges ($E$): Dependencies, transformations, and combinations between thought states.

## Generation Nodes
1. Branch $A$: Formulate initial approach focusing on core logic and minimal footprint.
2. Branch $B$: Formulate alternative approach prioritizing extensibility, edge-case coverage, and performance.
3. Branch $C$: Formulate fallback/defensive approach focusing on invariant preservation.

## Aggregation & Scoring
- Synthesize the strongest elements across Branches $A$, $B$, and $C$.
- Evaluate each candidate state using automated test validation: `{test_cmd}`.
- Score against repository invariants:
{invariants_text}

## Refinement & Exit Criteria
- Iterate on the combined candidate state until all failure gates pass with zero regressions.
- Deliver verified implementation and unit test assertions.
"""
    elif fw in ("META-PROMPTING", "METAPROMPTING"):
        body = f"""## Objective
Coordinate the execution of `{prompt_name}` in `{repo_name}` ({lang}) via meta-orchestration of fresh-context specialist agents.

## Conductor System Instructions
You are the Conductor. Analyze the overall task requirements and decompose `{prompt_name}` into mutually exclusive, collectively exhaustive subtasks.
Manage task handoffs without carrying unneeded conversational baggage into specialist contexts.

## Specialist Agent Personas
- **Specification & Contract Specialist**: Defines type boundaries, public APIs, and error contracts.
- **Implementation Specialist**: Writes minimal production logic matching the exact interface specifications.
- **Verification Specialist**: Constructs rigorous unit and boundary tests using `{test_cmd}`.

## Isolated Delegation Protocol
1. Dispatch each subtask with clear inputs and explicit completion criteria.
2. Ensure each specialist runs in isolation to prevent context pollution and attention dilution.
3. Validate each deliverable against repository guardrails:
{invariants_text}

## Synthesis & Verification
Synthesize the outputs from all specialist agents into a cohesive, verified patch. Run `{test_cmd}` to confirm overall integrity.
"""
    elif fw in ("BOT", "BUFFER-OF-THOUGHTS"):
        body = f"""## Objective
Solve `{prompt_name}` in `{repo_name}` ({lang}) by retrieving, distilling, and instantiating meta-thought templates from the reasoning buffer.

## Distilled Meta-Buffer Templates
Retrieve applicable problem-solving archetypes:
- **TDD Contract Template**: Interface Definition -> Failing Test -> Minimal Implementation -> Refactor.
- **Defensive Boundary Template**: Input Validation -> Core Transformation -> Safe Fallback / Error Handling.

## Problem Distillation
Distill the problem parameters and invariants for `{prompt_name}`:
{invariants_text}

## Instantiated Solution Steps
1. Instantiate the chosen meta-buffer template with `{repo_name}` specific context.
2. Execute step-by-step implementation adhering to distilled constraints.
3. Validate using `{test_cmd}`.

## Verification
Confirm solution satisfies both the distilled problem definition and general template invariants with zero regression.
"""
    elif fw == "MEDPROMPT":
        body = f"""## Objective
Execute high-precision reasoning and implementation for `{prompt_name}` in `{repo_name}` ({lang}) using the Medprompt methodology.

## Dynamic Few-Shot Exemplars
Retrieve domain-specific, structurally similar patterns from `{repo_name}` codebase:
- Exemplar A: Verified idiomatic pattern and test structure in existing suite.
- Exemplar B: Handling of boundary edge cases and failure modes.

## Chain-of-Thought Formulation
Develop detailed step-by-step reasoning connecting problem specification to target solution:
1. Break down domain rules and requirements.
2. Trace state mutations and edge case handling.
3. Validate against repository invariants:
{invariants_text}

## Choice-Shuffle Ensembling
- Generate multiple solution perspectives / variations by permuting option order or reasoning angles.
- Compare candidate solutions to eliminate positional and order bias.
- Select the consensus optimal implementation.

## Final Verification
Verify the selected consensus solution using `{test_cmd}` to ensure deterministic correctness.
"""
    elif fw in ("WEB-ACCESSIBLE", "WEB_ACCESSIBLE"):
        body = f"""## Context & Objective
Implement accessible, WCAG 2.2 AA compliant UI component `{prompt_name}` in `{repo_name}` ({lang}).

## Semantic Landmark Hierarchy
- Use semantic HTML landmarks (`<main>`, `<nav>`, `<header>`, `<article>`, `<button>`).
- Avoid unsemantic `<div>` wrapping and preserve natural document heading flow (`h1` through `h6`).

## Component Interface Stubs
Define typed props contract and exported boundary:
```typescript
interface {prompt_name.replace("-", "_").title().replace("_", "")}Props {{
  // Props contract
}}
```

## Keyboard & ARIA State Contracts
- Implement full keyboard interaction (`Tab`, `Shift+Tab`, `Escape`, `Enter`, `Space`).
- Manage dynamic ARIA states (`aria-expanded`, `aria-selected`, `aria-busy`, `aria-live`).
- Ensure visible focus indicator styling (`:focus-visible`).

## Responsive Layout Tokens
- Enforce fluid layout sizing using relative CSS units (`rem`, `em`, `clamp()`).

## Verification & Invariants
- Verify with `{test_cmd}` and screen-reader accessibility auditing.
{invariants_text}
"""
    elif fw in ("DEFENSIVE-ACTION", "DEFENSIVE_ACTION"):
        body = f"""## Context & Objective
Implement secure server action `{prompt_name}` in `{repo_name}` ({lang}) following defense-in-depth principles.

## Boundary Contract (Server Action)
- Explicit `'use server'` boundary directive at entry point.
- Zero leakage of server environment variables or database connection strings to the client.

## Runtime Schema (Zod)
- Validate and sanitize all client-submitted payloads at the boundary using runtime schemas.
- Reject unvalidated input before executing internal domain logic.

## Session Authorization (IDOR)
- Authenticate and resolve caller identity from secure server session.
- Verify ownership of target entity IDs to prevent Insecure Direct Object References.

## Database Query Isolation
- Parameterize all queries and avoid raw dynamic concatenation.
- Enforce isolation and transaction boundaries.

## Verification & Invariants
- Run `{test_cmd}` to verify boundary security tests.
{invariants_text}
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
            "cognitive": score.cognitive,
            "overall": score.overall,
        },
    }
    return meta, body
