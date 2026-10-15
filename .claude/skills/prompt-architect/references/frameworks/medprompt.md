# Medprompt / Dynamic Few-Shot Ensembling Framework

## Overview

Medprompt is a powerful composition of general-purpose prompting techniques designed to achieve frontier-grade precision without model fine-tuning. Originally created to evaluate generalist models on demanding medical licensing exams, Medprompt combines three foundational mechanisms:

1. **Dynamic $k$-NN Exemplar Retrieval**: Semantically retrieves the most relevant few-shot exemplars from a trusted offline bank using task query embeddings, ensuring context-specific grounding.
2. **Self-Generated Chain-of-Thought**: Generates detailed, step-by-step reasoning trajectories for every retrieved exemplar, providing structural demonstrations of rigorous problem-solving.
3. **Choice-Shuffle Ensembling**: Systematically permutes candidate options across multiple evaluation passes and aggregates predictions via plurality voting to neutralize positional bias and label token priors.

**Research basis:** Introduced in "Can Generalist Foundation Models Outcompete Special-Purpose Tuning? Case Study in Medicine" (Nori et al., Microsoft Research, 2023; arXiv:2311.16452). Medprompt achieved state-of-the-art results on all nine benchmark datasets of the MultiMedQA suite, surpassing models fine-tuned specifically on medical literature (such as Med-PaLM 2) by over 9%, and transferred with equal strength to electrical engineering, law, and philosophy benchmarks.

## The Algorithmic Triad

### 1. Dynamic Few-Shot Selection ($k$-NN Retrieval)
Standard few-shot prompting uses fixed, hand-curated exemplars. When test queries differ from the fixed set, the model receives suboptimal demonstrations. Medprompt indexes candidate exemplars using text embeddings (e.g., Ada/text-embedding-3) and retrieves the $k$ nearest neighbors to the test query via cosine similarity.

### 2. Self-Generated Chain-of-Thought (CoT)
Rather than requiring human experts to hand-author complex reasoning paths, the foundation model itself is prompted to generate step-by-step reasoning trajectories for the retrieved exemplars. Correct trajectories are verified against known answers and stored in the exemplar bank.

### 3. Choice-Shuffle Ensembling
Large language models suffer from pronounced **positional bias** (e.g., favoring Option A or Option D) and **label token bias**. Medprompt evaluates the problem multiple times with candidate options permuted across different orders (e.g., $[A, B, C, D] \rightarrow [B, D, A, C] \rightarrow [C, A, D, B]$), taking the consensus vote across all permutations.

## Components

### Dynamic Ensemble Specification
**Purpose:** Declare the high-assurance decision protocol, setting expectations for analytical rigor.

### Dynamic Exemplars ($k$-NN Retrieved)
**Purpose:** Inject semantically relevant exemplars with verified CoT reasoning trajectories and similarity scores.

### Active Challenge
**Purpose:** Present the target problem statement and candidate architectures or options under evaluation.

### Evaluation Protocol
**Purpose:** Direct the model through structured CoT reasoning, explicit candidate elimination, and schema-compliant final decision emission.

## Template Structure

This is the template as shipped in `assets/templates/medprompt_template.txt`:

```
[DYNAMIC ENSEMBLE SPECIFICATION]
You are a High-Assurance Decision Engine executing a Dynamic Few-Shot Reasoning Protocol.
Evaluate the problem using semantically grounded exemplar patterns and explicit step-by-step rationales.

[DYNAMIC EXEMPLARS (k-NN RETRIEVED)]
---
#### Exemplar 1 (Similarity Score: {sim_score_1})
Problem: {exemplar_problem_1}
Reasoning Trajectory: {exemplar_cot_1}
Conclusion: {exemplar_answer_1}
---
#### Exemplar 2 (Similarity Score: {sim_score_2})
Problem: {exemplar_problem_2}
Reasoning Trajectory: {exemplar_cot_2}
Conclusion: {exemplar_answer_2}
---

[ACTIVE CHALLENGE]
Problem Statement: {active_problem}
Candidate Options / Architectures:
{shuffled_candidates}

[EVALUATION PROTOCOL]
1. Step-by-Step Chain of Thought:
   - Identify active constraints and map analogies to the retrieved exemplars.
   - Formulate intermediate hypotheses and evaluate candidate viability.
2. Candidate Elimination & Scoring:
   - Provide explicit disproof or support for each candidate option.
3. Final Selection:
   - Emit the final selection matching the schema: `FINAL DECISION: <OPTION>`
```

## Complete Example

### Scenario: Database Isolation Level Selection for High-Frequency Ledger

**Before Medprompt:**
"What PostgreSQL transaction isolation level should we use for our account balance transfer service to prevent race conditions?"

**After Medprompt — Emitted Prompt:**
```markdown
[DYNAMIC ENSEMBLE SPECIFICATION]
You are a High-Assurance Decision Engine executing a Dynamic Few-Shot Reasoning Protocol.
Evaluate the database transaction isolation challenge using semantically grounded exemplar patterns and explicit step-by-step rationales.

[DYNAMIC EXEMPLARS (k-NN RETRIEVED)]
---
#### Exemplar 1 (Similarity Score: 0.93)
Problem: Selecting concurrency control for seat-reservation ticketing where double-booking must be strictly prevented under high burst traffic.
Reasoning Trajectory:
1. Under Read Committed, non-repeatable reads and phantom reads allow concurrent transactions to read the same available seat.
2. Under Repeatable Read, first-committer-wins prevents lost updates, but write skew can occur if constraints span multiple rows.
3. Serializable isolation guarantees execution equivalent to a serial order, completely eliminating write skew and phantom anomalies via predicate locking (SSI).
Conclusion: FINAL DECISION: SERIALIZABLE with client retry loop on 40001 serialization failure.
---
#### Exemplar 2 (Similarity Score: 0.88)
Problem: High-throughput inventory deduction with atomic counters where read-modify-write skew must be avoided without global locking.
Reasoning Trajectory:
1. Read Committed with conditional updates (`UPDATE ... WHERE balance >= amount`) utilizes row-level write locks.
2. However, multi-account ledger entries involve paired debit/credit updates across multiple rows.
3. When multiple rows must maintain zero-sum invariant, row-level locks on individual rows risk deadlocks and cross-row anomalies unless executed under Serializable or strict row-ordering.
Conclusion: FINAL DECISION: SERIALIZABLE with ordered row locks or SELECT FOR UPDATE.
---

[ACTIVE CHALLENGE]
Problem Statement:
Our fintech service executes multi-currency account transfers between sender and recipient. Requirements:
- Invariant: System-wide zero-sum balance integrity must never be violated.
- Concurrency: 5,000 transfers/sec across 200,000 active accounts.
- Problem: Mitigate write skew and phantom reads without table-level locking.

Candidate Options:
[A] READ COMMITTED with optimistic concurrency control version checks.
[B] REPEATABLE READ with automatic application retry.
[C] SERIALIZABLE using PostgreSQL SSI with exponential backoff on serialization errors.
[D] READ UNCOMMITTED with periodic reconciliation jobs.

[EVALUATION PROTOCOL]
1. Step-by-Step Chain of Thought:
   - Map analogies from Exemplars 1 & 2: multi-row balance constraints represent classic write skew risk.
   - Option [A] fails when transfers involve interdependent overdraft limits across accounts.
   - Option [B] prevents lost updates on individual rows but does NOT prevent write skew across multiple rows in PostgreSQL.
   - Option [D] allows dirty reads and violates zero-sum invariants immediately.
   - Option [C] uses SSI to detect rw-antidependencies and guarantees serializability without manual lock management.
2. Candidate Elimination & Scoring:
   - Disprove [A]: Inadequate cross-row isolation.
   - Disprove [B]: Susceptible to PostgreSQL write skew anomaly.
   - Disprove [D]: Disastrous data corruption.
   - Support [C]: Matches Exemplar 1 pattern exactly.
3. Final Selection:
   FINAL DECISION: [C] SERIALIZABLE using PostgreSQL SSI with exponential backoff on serialization errors.
```

## Best Use Cases

1. **High-Stakes Technical & Architectural Decisions**
   - Decisions where subtle flaws cause data loss, financial corruption, or security breaches.
2. **Domain-Specific Reasoning with Verified Exemplar Banks**
   - Legal, medical, financial, or complex systems questions with trusted past cases.
3. **Multi-Choice or Disambiguation Scenarios**
   - Evaluating trade-offs across 3–5 explicit design proposals.

## Selection Criteria

**Choose Medprompt when:**
- ✅ A bank of verified, structurally similar exemplars exists or can be dynamically retrieved.
- ✅ The task requires eliminating positional or formatting bias across candidate options.
- ✅ High accuracy and explicit disproof/support rationales are required.

**Avoid Medprompt when:**
- ❌ No similar exemplars exist or the task is completely novel exploration → use Tree of Thought or GoT.
- ❌ The task is writing code from scratch using live tools → use ReAct.
- ❌ The task is a quick, low-stakes text edit → use BAB or RTF.

## Common Mistakes

1. **Static Exemplars**: Hardcoding the same generic examples for every query instead of retrieving semantically close exemplars ($k$-NN).
2. **Omitting the Choice Shuffle**: Evaluating candidates in only one fixed order, allowing positional bias to skew results.
3. **Unverified Exemplar CoT**: Feeding incorrect or hand-wavy reasoning trajectories into the few-shot demonstrations.

## Quick Reference

| Component | Purpose | Key Metric |
|---|---|---|
| $k$-NN Retrieval | Find semantically closest problem patterns | Cosine similarity ($\ge 0.80$) |
| Self-Generated CoT | Demonstrate rigorous step-by-step deduction | Sound intermediate deductions |
| Choice Shuffle | Neutralize candidate order and label token bias | Majority/plurality consensus |
| Elimination & Verdict | Explicitly disprove invalid options before emitting decision | Zero-ambiguity selection |
