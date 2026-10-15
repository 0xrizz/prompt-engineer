# Graph-of-Thoughts (GoT) Framework

## Overview

Graph-of-Thoughts (GoT) extends beyond linear Chain-of-Thought and tree-structured exploration by modeling the reasoning process as an arbitrary Directed Acyclic Graph (DAG) $G = (V, E)$. In GoT, vertices ($V$) represent distinct thought states (hypotheses, partial architectural slices, algorithm components), and directed edges ($E$) encode dependencies, transformations, combinations, and feedback loops between thought states.

Where Chain-of-Thought follows a single linear path ($T_1 \rightarrow T_2 \rightarrow T_3$) and Tree-of-Thoughts explores isolated branches without path recombination ($T_0 \rightarrow \{T_{1a}, T_{1b}\}$), Graph-of-Thoughts enables multiple distinct thought branches to merge via `Aggregate` and iterate via in-place `Refine` operations.

**Research basis:** Introduced in "Graph of Thoughts: Solving Elaborate Problems with Large Language Models" (Besta et al., ETH Zürich, AAAI 2024; arXiv:2308.09687). The authors demonstrate that modeling thought processes as arbitrary graphs outperforms Tree-of-Thoughts across diverse reasoning tasks—improving sorting quality by 62% over ToT while reducing execution costs by over 31%.

## Core Algorithmic Operators

Graph-of-Thoughts defines four foundational thought transformation operators:

1. **`Generate(t)`**: Produces $k$ successor thoughts from an existing thought node $t$. Used during the initial divergence stage to explore orthogonal approaches.
2. **`Aggregate(t_1, t_2, ...)`**: Synergistically synthesizes multiple disparate thoughts into a unified composite thought, merging complementary strengths while resolving contradictory assumptions.
3. **`Refine(t)`**: Executes an in-place feedback iteration on an existing thought based on diagnostic evaluation or error traces.
4. **`Score(t) -> s`**: Computes an objective scalar quality score $s \in [0, 1]$ evaluating node utility against stated constraints and invariants.

## Components

### Problem Specification
**Purpose:** Formulate the core challenge, input constraints, non-negotiable invariants, and success metrics.

### Graph Topology & Generation Nodes
**Purpose:** Establish the DAG structure and generate competing initial solution branches across orthogonal design dimensions.

**Questions to Ask:**
- What are the mutually independent candidate approaches?
- What trade-offs differentiate Branch A, Branch B, and Branch C?
- What dimensions of variation matter (latency, safety, memory, maintainability)?

### Cross-Branch Scoring & Pruning
**Purpose:** Systematically evaluate each candidate vertex against the constraint set using explicit scoring criteria and eliminate non-viable nodes.

### Synergistic Aggregation ($V_{AGG} = V_x \oplus V_y$)
**Purpose:** Combine the strongest elements of surviving candidate nodes into a unified composite architecture.

### Refinement & Verification Loop ($V_{FINAL} = \text{Refine}(V_{AGG})$)
**Purpose:** Audit the composite node for edge cases, apply surgical diagnostic patches, and emit the verified final deliverable.

## Template Structure

This is the template as shipped in `assets/templates/got_template.txt`:

```
[ROLE & GRAPH OBJECTIVE]
You are a Principal Systems Architect executing a Graph-of-Thoughts (GoT) reasoning protocol.
Your objective is to solve the target challenge by modeling your reasoning as a Directed Acyclic Graph (DAG) with explicit aggregation and refinement operators.

[PROBLEM SPECIFICATION]
{problem_statement}

[GRAPH EXECUTION STAGES]
Execute and label each graph operation explicitly:

### STAGE 1: PARALLEL GENERATION (V1, V2, V3)
Decompose the challenge into independent sub-problems. Generate discrete, competing thought vertices:
- Vertex V1 (Approach A / Domain Focus 1): [Formulate independent candidate solution]
- Vertex V2 (Approach B / Domain Focus 2): [Formulate independent candidate solution]
- Vertex V3 (Approach C / Domain Focus 3): [Formulate independent candidate solution]

### STAGE 2: CROSS-BRANCH SCORING & PRUNING
Evaluate each thought vertex against the non-negotiable constraints:
- Score(V1): [0.0 - 1.0] | Failure modes / Tradeoffs: [Brief critique]
- Score(V2): [0.0 - 1.0] | Failure modes / Tradeoffs: [Brief critique]
- Score(V3): [0.0 - 1.0] | Failure modes / Tradeoffs: [Brief critique]
Prune vertices failing boundary conditions.

### STAGE 3: SYNERGISTIC AGGREGATION (V_AGG = V_x ⊕ V_y)
Synthesize the surviving vertices into an integrated composite architecture:
- Combine complementary strengths while resolving conflicting boundary assumptions.
- Construct the aggregate thought node V_AGG.

### STAGE 4: REFINEMENT & VERIFICATION LOOP (V_FINAL = Refine(V_AGG))
Audit V_AGG against edge cases and system invariants:
- Diagnostic Check: [Identify remaining vulnerabilities or oversights]
- Refinement Patch: [Apply surgical corrections]
- Emit the consolidated final output.
```

## Complete Example

### Scenario: High-Throughput Distributed Cache Architecture

**Before GoT:**
"Design a caching layer for our user profile service that handles 100k QPS with sub-5ms p99 latency."

**After GoT — Emitted Prompt:**
```markdown
[ROLE & GRAPH OBJECTIVE]
You are a Principal Systems Architect executing a Graph-of-Thoughts (GoT) reasoning protocol.
Your objective is to design a resilient caching layer for a user profile service handling 100k QPS under sub-5ms p99 latency constraints by modeling reasoning as a Directed Acyclic Graph (DAG).

[PROBLEM SPECIFICATION]
- Scale: 100,000 QPS read traffic, 2,000 QPS write traffic.
- Latency SLO: p99 < 5ms.
- Data Volume: 50 million active profiles (~2KB payload per profile = ~100GB total working set).
- Invariants: Zero stale reads exceeding 3 seconds, automatic fallback during network partition, minimal GC pause impact.

[GRAPH EXECUTION STAGES]

### STAGE 1: PARALLEL GENERATION (V1, V2, V3)
Decompose into three distinct architectural paradigms:
- Vertex V1 (Pure Distributed Redis Cluster): Large centralized cluster with consistent hashing.
- Vertex V2 (Tiered Local L1 + Remote L2 Cache): In-process L1 (Caffeine / LRU) backed by Redis L2.
- Vertex V3 (Read-Through Embedded Key-Value Storage): Local RocksDB/LMDB replicated via Raft.

### STAGE 2: CROSS-BRANCH SCORING & PRUNING
Evaluate V1, V2, V3 against latency, consistency, and operational complexity:
- Score(V1): 0.72 | Network round-trip per request risks 5ms p99 under high network saturation.
- Score(V2): 0.91 | In-process L1 guarantees <0.5ms reads; invalidation complexity across instances is manageable with Pub/Sub.
- Score(V3): 0.65 | Embedded storage eliminates network hop but introduces heavy storage replication overhead and pod memory pressure.
Pruning Decision: Prune V3 due to operational overhead; retain V1 and V2.

### STAGE 3: SYNERGISTIC AGGREGATION (V_AGG = V1 ⊕ V2)
Combine V1 (distributed centralized authority) and V2 (ultra-low latency in-process caching):
- Layer 1: In-process bounded LRU (max 10,000 hottest keys per node, 5-second TTL).
- Layer 2: Sharded Redis Cluster with read replicas for cold keys.
- Invalidation Bus: Redis Streams with consumer groups broadcasting cache invalidation events to L1 instances.

### STAGE 4: REFINEMENT & VERIFICATION LOOP (V_FINAL = Refine(V_AGG))
Audit V_AGG against thundering herd and partition edge cases:
- Diagnostic: If Redis Cluster experiences transient network blip, L1 cache misses could stampede the backing PostgreSQL database.
- Refinement Patch: Add probabilistic early expiration (XFetch algorithm) in L1 and a distributed single-flight mutex across nodes.
- Deliver final architectural specification and verification checklist.
```

## Best Use Cases

1. **Complex System Architecture & Trade-Off Analysis**
   - Synthesizing architectures where no single off-the-shelf approach satisfies all constraints.
2. **Algorithm & Multi-Phase Refactoring**
   - Combining fast approximate algorithms with exact fallback routines.
3. **Multi-Branch Problem Decomposition**
   - Tasks requiring parallel exploration of independent sub-components followed by synthesis.

## Selection Criteria

**Choose Graph-of-Thoughts when:**
- ✅ The problem has multiple valid sub-approaches that should be combined rather than chosen exclusively.
- ✅ Solution paths exhibit interdependencies and benefit from cross-pollination.
- ✅ Candidate states can be objectively scored and iteratively refined against error diagnostics.

**Avoid Graph-of-Thoughts when:**
- ❌ The task is linear and step-by-step → use Chain of Thought or Plan-and-Solve.
- ❌ Branches are mutually exclusive alternatives to compare once → use Tree of Thought.
- ❌ The problem matches a standard known algorithmic archetype → use Buffer-of-Thoughts.
- ❌ External tools and runtime feedback drive the trajectory → use ReAct.

## GoT vs. Chain of Thought vs. Tree of Thoughts

| Dimension | Chain of Thought (CoT) | Tree of Thoughts (ToT) | Graph of Thoughts (GoT) |
|---|---|---|---|
| Topology | Linear chain ($1 \rightarrow 1$) | Tree hierarchy ($1 \rightarrow N$) | Arbitrary DAG ($N \rightarrow M$) |
| Branch Combination | None | None (isolated paths) | **Yes (`Aggregate`)** |
| In-Place Feedback | None | Backtracking | **Yes (`Refine`)** |
| State Evaluation | Implicit | Heuristic scoring | **Quantitative scoring** |
| Complexity | Low | Medium | High |

## Common Mistakes

1. **Omitting the Aggregation Operator**: Treating GoT like Tree-of-Thoughts by picking a single branch rather than synthesizing complementary strengths across branches.
2. **Skipping Pruning**: Carrying low-scoring, infeasible branches into the aggregation stage, diluting output quality.
3. **Lack of Objective Scoring**: Using subjective adjectives instead of explicit scores and constraint checklists.
4. **Neglecting Convergence Criteria**: Allowing refinement loops to continue without a clear exit threshold.

## Quick Reference

| Stage | Operation | Core Question |
|---|---|---|
| Stage 1 | Parallel Generation (`Generate`) | "What are 3 distinct, valid approaches to this problem?" |
| Stage 2 | Scoring & Pruning (`Score`) | "Which approaches satisfy all hard invariants?" |
| Stage 3 | Aggregation (`Aggregate`) | "How can we combine the best features of surviving branches?" |
| Stage 4 | Refinement (`Refine`) | "What edge cases remain and how do we surgically patch them?" |
