# Meta-Prompting Framework

## Overview

Meta-Prompting is a task-agnostic scaffolding framework that transforms a language model into an authoritative meta-orchestrator ("The Conductor"). Rather than attempting to solve a multi-faceted problem in a single pass or simulating a crowded conversation within a single context window, Meta-Prompting:
1. Decomposes the complex objective into mutually independent, collectively exhaustive subtasks.
2. Allocates specialized expert personas to each subtask.
3. Dispatches each query to an isolated, fresh zero-state context to prevent context pollution and attention dilution.
4. Critically audits each specialist's findings for mutual consistency and boundary compliance.
5. Synthesizes a unified, verified response.

**Research basis:** Introduced in "Meta-Prompting: Enhancing Language Models with Task-Agnostic Scaffolding" (Suzgun & Kalai, Harvard University & Microsoft Research, 2024; arXiv:2401.12954). Meta-Prompting significantly outperformed standard zero-shot prompting, dynamic few-shot CoT, and expert-persona prompting across challenging tasks including Game of 24 (100% vs 74% with Tree-of-Thought), Python code generation, and multi-domain reasoning benchmarks.

## Discriminating Contrast: Meta-Prompting vs. Standard Multi-Persona

Standard multi-persona prompting simulates an in-context committee dialogue (e.g., "Act as an Architect, Security Reviewer, and QA Engineer talking to each other in one thread"). In practice, this induces severe failure modes:
- **Context Pollution**: Conversational banter, preliminary errors, and tokens from persona A degrade the attention budget of persona B.
- **Mutual Hallucination Cascades**: When persona A makes a subtle factual error, persona B adopts it as ground truth.
- **Role Collapse**: Over extended turns, distinct expert personas converge toward generic model defaults.

Meta-Prompting enforces strict **context isolation**: each specialist operates in a zero-state context receiving only its precise input contract, and the Conductor is the sole arbiter of state and synthesis.

## Algorithmic Mechanics

1. **Task Analysis & Decomposition**: The Conductor breaks the root directive into decoupled sub-problems with explicit input/output boundaries.
2. **Fresh-Context Specialist Allocation**: Each sub-problem receives a tailored domain expert persona (e.g., Cryptographic Security Specialist, Distributed Storage Engineer).
3. **Execution & Tool Verification**: Each specialist independently executes its mandate without distraction.
4. **Critical Audit & Cross-Verification**: The Conductor examines the returned deliverables, cross-checking parameters, checking for contradictory assumptions, and enforcing hard invariants.
5. **Unified Synthesis**: The Conductor reconciles verified contributions into a cohesive master deliverable.

## Components

### Orchestrator / Conductor Directive
**Purpose:** Establish the top-level orchestration role, delegating authority, and synthesis responsibility.

### Task Directive
**Purpose:** Define the overarching problem, scope, constraints, and target deliverables.

### Phase 1: Decomposition & Specialist Allocation
**Purpose:** Partition the task into decoupled subtasks and specify the exact persona and competence required for each.

### Phase 2: Isolated Specialist Consultations
**Purpose:** Execute isolated specialist inquiries. Each inquiry contains a targeted query and captures the expert output.

### Phase 3: Critical Audit & Cross-Verification
**Purpose:** Identify parameter mismatches, edge case oversights, or conflicting boundaries across specialist outputs.

### Phase 4: Unified Synthesis
**Purpose:** Construct the final verified deliverable integrating all approved specialist solutions.

## Template Structure

This is the template as shipped in `assets/templates/meta_prompting_template.txt`:

```
[ORCHESTRATOR / CONDUCTOR DIRECTIVE]
You are the Central Conductor of an advanced Meta-Prompting orchestration engine. 
Your role is to orchestrate, delegate to, and synthesize outputs from isolated specialized expert instances to achieve a verified, multi-perspective solution.

[TASK DIRECTIVE]
{task_directive}

[CONDUCTOR EXECUTION PROTOCOL]
Execute the orchestration using the following phased structure:

### PHASE 1: DECOMPOSITION & SPECIALIST ALLOCATION
Break down the task into discrete, decoupled sub-problems. Specify the specialized expert persona required for each:
- Sub-Task A: Assigned Specialist: [Persona & Core Competency]
- Sub-Task B: Assigned Specialist: [Persona & Core Competency]
- Sub-Task C: Assigned Specialist: [Persona & Core Competency]

### PHASE 2: ISOLATED SPECIALIST CONSULTATIONS
Execute each consultation assuming a completely isolated, clean context:

---
#### CONSULTATION A: [Specialist Persona Name]
Query: [Precise sub-problem instruction]
Expert Output:
[Detailed expert reasoning and solution]
---
#### CONSULTATION B: [Specialist Persona Name]
Query: [Precise sub-problem instruction]
Expert Output:
[Detailed expert reasoning and solution]
---
#### CONSULTATION C: [Specialist Persona Name]
Query: [Precise sub-problem instruction]
Expert Output:
[Detailed expert reasoning and solution]
---

### PHASE 3: CRITICAL AUDIT & CROSS-VERIFICATION
As the Conductor, audit the specialist outputs:
1. Identify any contradictions, parameter mismatches, or overlooked constraints between consultations.
2. Verify adherence to system invariants and technical boundaries.

### PHASE 4: UNIFIED SYNTHESIS
Produce the final, integrated deliverable reconciling all specialist contributions into a coherent response.
```

## Complete Example

### Scenario: Secure Payment Webhook Ingestion Service

**Before Meta-Prompting:**
"Write a secure webhook handler for Stripe payments in Next.js with database updates and user notifications."

**After Meta-Prompting — Emitted Prompt:**
```markdown
[ORCHESTRATOR / CONDUCTOR DIRECTIVE]
You are the Central Conductor of an advanced Meta-Prompting orchestration engine. 
Your role is to orchestrate, delegate to, and synthesize outputs from isolated specialized expert instances to design a production-grade, hardened payment webhook ingestion service in Next.js App Router and TypeScript.

[TASK DIRECTIVE]
Implement `POST /api/webhooks/stripe` handling `checkout.session.completed` events:
- Invariants: Idempotent processing, cryptographic signature verification, zero secret leakage, safe database transactions, and deterministic event deduplication.

[CONDUCTOR EXECUTION PROTOCOL]

### PHASE 1: DECOMPOSITION & SPECIALIST ALLOCATION
- Sub-Task A (Cryptographic Boundary): Stripe signature validation and raw body parsing in Next.js App Router.
  Specialist: Security & Web Boundary Specialist.
- Sub-Task B (Data Consistency & Idempotency): Idempotency key locking, atomic database transactions with Prisma.
  Specialist: Distributed Database Architect.
- Sub-Task C (Telemetry & Failure Recovery): Dead-letter queuing, structured logging, alert metrics.
  Specialist: SRE & Observability Specialist.

### PHASE 2: ISOLATED SPECIALIST CONSULTATIONS

---
#### CONSULTATION A: Security & Web Boundary Specialist
Query: Define the exact boundary middleware to verify `stripe-signature` without buffering entire payloads in memory, handling replay attacks with 5-minute timestamp tolerance.
Expert Output:
Uses `stripe.webhooks.constructEvent` with `req.text()`, checks signature header, and rejects with 400 immediately on mismatch.

---
#### CONSULTATION B: Distributed Database Architect
Query: Design the database schema and idempotent transaction strategy for processing `checkout.session.completed`.
Expert Output:
Employs an `InboundEvent` table with unique constraint on `stripe_event_id`. Uses PostgreSQL advisory locks or `ON CONFLICT DO NOTHING` inside a serializable transaction to prevent double-crediting.

---
#### CONSULTATION C: SRE & Observability Specialist
Query: Design error handling, retry backoff protocols, and metric emissions.
Expert Output:
Emits OpenTelemetry spans, records Stripe event ID and processing duration, and returns 200 on duplicate events to prevent Stripe retry storms.

---

### PHASE 3: CRITICAL AUDIT & CROSS-VERIFICATION
The Conductor cross-checks Specialist outputs:
1. Body parsing alignment: Specialist A used `await req.text()`. Confirmed Next.js Route Handlers allow single-pass text consumption.
2. Error code contract: Specialist B suggested throwing 500 on duplicate event, but Specialist C noted that returning 500 causes Stripe to resend webhooks indefinitely. Conductor reconciles: Duplicate event is logged as 200 OK with `processed: false`.
3. Invariants confirmed: Zero leakage of `STRIPE_WEBHOOK_SECRET` to client components.

### PHASE 4: UNIFIED SYNTHESIS
Emit the consolidated Next.js route handler, Prisma migration, and end-to-end integration test suite.
```

## Best Use Cases

1. **Multi-Discipline Engineering Tasks**
   - Features requiring simultaneous domain expertise (security + database + frontend + DevOps).
2. **High-Stakes Architecture Reviews**
   - Independent security, performance, and maintainability audits prior to implementation.
3. **Complex Systems Decomposition**
   - Projects that naturally split into autonomous subtasks with well-defined contracts.

## Selection Criteria

**Choose Meta-Prompting when:**
- ✅ The task involves distinct areas of expertise that conflict when mixed in a single context.
- ✅ Independent validation, cross-auditing, and reconciliation are critical.
- ✅ The overall problem is too large or complex for a single prompt pass.

**Avoid Meta-Prompting when:**
- ❌ The task is a simple single-domain script → use RISEN or RTF.
- ❌ The workflow requires step-by-step tool feedback in an emergent environment → use ReAct.
- ❌ The goal is exploring candidate branches with aggregation in one model call → use Graph-of-Thoughts.

## Common Mistakes

1. **Simulating Banter Instead of Work**: Letting specialists talk to each other instead of reporting clean deliverables to the Conductor.
2. **Missing Conductor Audit (Phase 3)**: Blindly concatenating specialist answers without resolving contradictions or verifying system invariants.
3. **Leaking Context Across Specialists**: Including the entire conversation history in specialist queries instead of scoped sub-problem inputs.

## Quick Reference

| Phase | Responsibility | Key Output |
|---|---|---|
| Phase 1: Decomposition | Decompose task into decoupled subtasks | Subtask list & expert persona assignments |
| Phase 2: Consultations | Isolated expert executions in zero-state context | Focused, expert technical deliverables |
| Phase 3: Critical Audit | Reconcile contradictions and verify invariants | Identified gaps and alignment fixes |
| Phase 4: Synthesis | Build the unified, verified solution | Final production deliverable |
