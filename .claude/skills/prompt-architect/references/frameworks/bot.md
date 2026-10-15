# Buffer-of-Thoughts (BoT) Framework

## Overview

Buffer-of-Thoughts (BoT) is a thought-augmented reasoning paradigm that retrieves, parameterizes, and instantiates pre-distilled high-level **thought-templates** from a persistent meta-buffer. Rather than performing costly, ad-hoc search from scratch on every run (as done in Tree-of-Thoughts or Graph-of-Thoughts), Buffer-of-Thoughts leverages past problem-solving archetypes, dramatically accelerating reasoning while improving precision.

By identifying the structural archetype of a problem upfront, BoT reduces reasoning latency and token expenditure to **~12% of combinatorial search frameworks** while outperforming zero-shot CoT and multi-query ensembling on standard reasoning benchmarks.

**Research basis:** Introduced in "Buffer of Thoughts: Thought-Augmented Reasoning with Large Language Models" (Yang et al., Peking University & UC Berkeley, NeurIPS 2024 Spotlight; arXiv:2406.04271). BoT achieves significant performance improvements across mathematical, algorithmic, and general reasoning tasks (averaging +11% to +50% gains over standard prompting) with an order-of-magnitude reduction in inference compute compared to ToT/GoT.

## Core Architectural Components

1. **Meta-Buffer**: A curated, persistent collection of abstracted thought-templates categorized by algorithmic, structural, and architectural archetypes.
2. **Thought-Retriever**: A semantic matching mechanism that compares the topology of an incoming problem against the meta-buffer to select the optimal archetype.
3. **Thought-Instantiator**: Translates the abstract schema into an actionable, concrete solution path by binding specific domain parameters, invariants, and variables.
4. **Buffer-Manager**: Continuously distills and refines thought-templates from successful problem executions to expand the buffer's capability.

## Standard Structural Archetypes

- **Divide-and-Conquer Template**: Problem partitioning into non-overlapping subproblems, independent resolution, and recombination.
- **State Transition Machine Template**: Explicit state-space definitions, valid transitions, guard conditions, and deterministic termination.
- **Two-Pointer / Sliding Window Invariant Template**: Monotonic pointer progression, window boundary conditions, and invariant preservation.
- **Constraint Satisfaction & Pruning Template**: Variable domain bounds, forward checking, failure propagation, and backtrack pruning.
- **TDD Contract Template**: Interface contract definition, minimal failing test, minimal implementation, refactor and invariant validation.

## Components

### Input Problem
**Purpose:** State the problem description, target constraints, and input data.

### Step 1: Archetype Retrieval
**Purpose:** Classify the problem's underlying structure and select the corresponding thought-template.

### Step 2: Thought-Template Specification
**Purpose:** Detail the formal schema: state space, transition/decomposition rules, and boundary conditions.

### Step 3: Template Instantiation
**Purpose:** Substitute the concrete problem variables into the abstract schema and execute step-by-step reasoning.

### Step 4: Verification & Summary
**Purpose:** Validate the instantiated output against all constraints and emit the final deliverable.

## Template Structure

This is the template as shipped in `assets/templates/bot_template.txt`:

```
[ROLE & REASONING BUFFER INSTRUCTION]
You are an Advanced Reasoning Engine operating under the Buffer-of-Thoughts (BoT) paradigm.
Rather than attempting ad-hoc generation, identify the underlying structural archetype, instantiate the corresponding thought-template, and execute the concrete solution.

[INPUT PROBLEM]
{problem_statement}

[BUFFER EXECUTION PIPELINE]

### STEP 1: ARCHETYPE RETRIEVAL
Analyze the input problem and retrieve the best-matching structural thought-template:
- Identified Archetype: [e.g., Divide-and-Conquer | State Transition Machine | Constraint Satisfaction | Two-Pointer Invariant]
- Rationale: [Why this structural archetype matches the problem topology]

### STEP 2: THOUGHT-TEMPLATE SPECIFICATION
Formulate the abstract reasoning schema for this archetype:
- State Space Definition: [Define variables, bounds, and invariables]
- Transition / Decomposition Rules: [Define step-by-step transformation rules]
- Boundary & Termination Conditions: [Define exact halting and validity criteria]

### STEP 3: TEMPLATE INSTANTIATION
Bind the specific entities, parameters, and data from the input problem into the abstract schema:
- Concrete State Bindings: [Map input values into schema]
- Step-by-Step Executed Transformations: [Walk through the instantiated reasoning steps]

### STEP 4: VERIFICATION & SUMMARY
Verify the solution against all stated boundary conditions:
- Solution Validation: [Programmatic or logical confirmation]
- Final Output: [Emit the clean, unambiguous result]
```

## Complete Example

### Scenario: Sliding Window Rate Limiter with Burst Allowance

**Before BoT:**
"Write an algorithm in Python to implement rate limiting allowing 100 requests per minute with bursts up to 20 requests."

**After BoT — Emitted Prompt:**
```markdown
[ROLE & REASONING BUFFER INSTRUCTION]
You are an Advanced Reasoning Engine operating under the Buffer-of-Thoughts (BoT) paradigm.
Identify the underlying structural archetype, instantiate the corresponding thought-template, and execute a verified Python implementation for a Sliding Window Log Rate Limiter.

[INPUT PROBLEM]
Design a high-throughput, memory-efficient sliding-window rate limiter in Python:
- Capacity: 100 requests per rolling 60-second window.
- Burst Allowance: Up to 20 requests within any 5-second sub-window.
- Invariants: Thread-safe, minimal lock contention, automatic eviction of expired entries, $O(1)$ amortized per-request overhead.

[BUFFER EXECUTION PIPELINE]

### STEP 1: ARCHETYPE RETRIEVAL
- Identified Archetype: Sliding Window Invariant with Monotonic Timestamp Deque.
- Rationale: The problem requires evaluating counts within sliding temporal windows without discrete boundary cliff-effects.

### STEP 2: THOUGHT-TEMPLATE SPECIFICATION
- State Space Definition:
  - `history_60s`: double-ended queue storing monotonic timestamps of events in $[now - 60s, now]$.
  - `history_5s`: double-ended queue storing timestamps of events in $[now - 5s, now]$.
  - `lock`: threading.Lock protecting queue operations.
- Transition Rules:
  - On `acquire(now)`:
    1. Pop timestamps from left of `history_60s` where $t < now - 60.0$.
    2. Pop timestamps from left of `history_5s` where $t < now - 5.0$.
    3. Check `len(history_60s) < 100` AND `len(history_5s) < 20`.
    4. If true: append `now` to both deques; return `True`.
    5. Else: reject; return `False`.
- Boundary Conditions:
  - Clock skew: assume monotonic timestamps via `time.monotonic()`.
  - Empty queues: immediate pass.

### STEP 3: TEMPLATE INSTANTIATION
Bind concrete Python datatypes and implement the thread-safe `SlidingWindowLimiter` class:
```python
from collections import deque
import threading
import time

class SlidingWindowLimiter:
    def __init__(self, limit_60s: int = 100, burst_5s: int = 20) -> None:
        self.limit_60s = limit_60s
        self.burst_5s = burst_5s
        self.history_60s = deque()
        self.history_5s = deque()
        self.lock = threading.Lock()

    def allow(self) -> bool:
        now = time.monotonic()
        with self.lock:
            # 1. Evict expired
            cutoff_60 = now - 60.0
            while self.history_60s and self.history_60s[0] <= cutoff_60:
                self.history_60s.popleft()

            cutoff_5 = now - 5.0
            while self.history_5s and self.history_5s[0] <= cutoff_5:
                self.history_5s.popleft()

            # 2. Evaluate boundaries
            if len(self.history_60s) < self.limit_60s and len(self.history_5s) < self.burst_5s:
                self.history_60s.append(now)
                self.history_5s.append(now)
                return True
            return False
```

### STEP 4: VERIFICATION & SUMMARY
- Bound Verification: `len(history_60s)` strictly bounded by 100; burst bounded by 20.
- Thread-Safety: Atomic check-then-act guarded by lock.
- Clean Output: Deliver implementation with unit test fixtures.
```

## Best Use Cases

1. **Algorithmic & Data Structure Design**
   - Problems matching recognized patterns (trees, graphs, DP, two pointers, state machines).
2. **Production Systems Infrastructure**
   - Rate limiters, connection pools, stateful stream processors, cache eviction strategies.
3. **High-Frequency Engineering Queries**
   - Repetitive problem types where searching from scratch wastes time and tokens.

## Selection Criteria

**Choose Buffer-of-Thoughts when:**
- ✅ The problem matches an established structural, algorithmic, or architectural archetype.
- ✅ Low latency and minimal token consumption are paramount.
- ✅ A proven template guarantees correct invariant handling without combinatorial trial and error.

**Avoid Buffer-of-Thoughts when:**
- ❌ The problem is open-ended and requires exploring novel branching alternatives → use Tree of Thought or Graph of Thoughts.
- ❌ The task involves cross-functional specialist orchestration → use Meta-Prompting.
- ❌ The task requires interactive, live tool execution in a loop → use ReAct.

## BoT vs. Tree of Thoughts vs. Chain of Thought

| Dimension | Chain of Thought (CoT) | Tree of Thoughts (ToT) | Buffer of Thoughts (BoT) |
|---|---|---|---|
| Approach | Linear step-by-step | Combinatorial search tree | **Template retrieval & instantiation** |
| Latency | Low | Very High | **Low (~12% of ToT)** |
| Cost | Minimal | High (many calls) | **Minimal (single-call instantiation)** |
| Structural Rigor | Variable | High | **Extremely High (formally grounded)** |

## Common Mistakes

1. **Force-Fitting the Wrong Archetype**: Selecting a template that doesn't match the problem invariants (e.g., using greedy pointer logic when dynamic programming is required).
2. **Skipping the Formal Template Specification (Step 2)**: Jumping straight from archetype name to code without specifying state space and transitions.
3. **Neglecting Boundary Invariants**: Failing to instantiate termination or eviction conditions in Step 3.

## Quick Reference

| Step | Objective | Primary Artifact |
|---|---|---|
| Step 1: Archetype Retrieval | Identify underlying structural archetype | Archetype name & match rationale |
| Step 2: Template Specification | Define state space and transition rules | Formal abstract reasoning schema |
| Step 3: Template Instantiation | Map concrete problem data into schema | Working step-by-step implementation |
| Step 4: Verification | Check invariants and validate correctness | Verified deliverable |
