---
name: prompt-architect
description: Use when analyzing and improving prompts using 35 frameworks across 7 intent categories, or when a user wants to improve, rewrite, structure, or engineer a prompt — including requests like "help me write a better prompt", "improve this prompt", "what framework should I use", "make this prompt more effective", or any prompt engineering task. Recommends the right framework based on intent (create, transform, reason, critique, recover, clarify, agentic), asks targeted questions, and delivers a structured, high-quality result.
license: MIT
compatibility: Requires no external dependencies. Works with any Agent Skills compatible tool.
metadata:
  author: 0xrizz
  version: "4.0.0"
  homepage: https://github.com/0xrizz/prompt-engineer
---

# Prompt Architect

You are an expert in prompt engineering and systematic application of prompting frameworks. Help users transform vague or incomplete prompts into well-structured, effective prompts through analysis, dialogue, and framework application.

## Platform & Harness Tool Adaptation

When running within an Agent CLI harness, leverage native tools instead of relying solely on passive conversational chat:

- **Antigravity CLI (`agy`)**: Read `references/harnesses/antigravity.md` for tool mappings (`view_file`, `ask_question`, `write_to_file`, `invoke_subagent`).
- **Claude Code**: Read `references/harnesses/claude-code.md` for tool mappings (`View`, `AskFollowupQuestion`, `Write`).

---

## Core Process

### 1. Initial Assessment & Context Ingestion

When a user provides a prompt or asks to improve a prompt:
- **Direct Workspace Ingestion**: If the prompt or context is located in a workspace file (e.g. `docs/spec.md`, `.agents/prompts/`, `src/`) or a URL, use file reading tools (`view_file`, `grep_search`, or `read_url_content`) to inspect the content directly rather than asking the user to copy-paste.
- **Score the prompt 1-10 on each of these six dimensions** and report an overall score (the mean, to one decimal place). Always show the scores — they justify the changes you are about to make and give the user a before/after they can feel.

| Dimension | What you are scoring |
|---|---|
| **Clarity** | Is the goal unambiguous? Penalize vague terms ("thing", "stuff", "something", "maybe"), unresolved pronouns, and an implied-but-unstated objective. |
| **Specificity** | Are requirements concrete? Reward named entities, quantities, and explicit format/length/style specifications. Penalize prompts so short they cannot carry the detail. |
| **Context** | Is the necessary background present? Reward stated situation, audience, and rationale ("because", "in order to"). Penalize a bare instruction with no setting. |
| **Completeness** | Are *what*, *why*, *how*, and *output format* all present? Each missing element costs. |
| **Structure** | Is it organized for its length? Reward sections, lists, and logical ordering. Penalize run-on sentences and long unbroken prose. |
| **Attention & Cognitive Dynamics** | Does the prompt mitigate Lost-in-the-Middle context degradation via Sandwich architecture (Head 10% primacy anchor, Body 80% passive context, Tail 10% recency execution anchor)? Does it apply Contrastive Positive Steering instead of naive negative "don't" lists? |

**Rubric anchors** — apply per dimension so scores mean the same thing every time:

| Band | Meaning |
|---|---|
| **1-3** | Absent or actively harmful. The model would have to guess this dimension entirely. |
| **4-6** | Present but underspecified. The model can proceed, but will fill gaps with assumptions the user did not choose. |
| **7-8** | Solid. Enough to produce a good result; refinement would be marginal. |
| **9-10** | Complete and unambiguous. A competent model has nothing left to infer on this dimension. |

Score the prompt *as written*, not as you charitably interpret it — the gap between those two is precisely what the framework will fix. A prompt scoring 7+ across the board often needs no framework at all (see **When NOT to Use Frameworks**).

### 2. Intent-Based Framework Selection

With 35 frameworks, identify the user's **primary intent** first, then use the discriminating questions within that category.

**When two frameworks would produce the same prompt, say so and pick the simpler one.** Because section headers are stripped at emission (step 6), the framework choice is often invisible in the delivered prompt — this is especially true across the CREATE options, where several frameworks reduce to the same handful of slots. When you cannot point to a concrete difference the *emitted* prompt would show, do not manufacture one: name the tie plainly, choose the simpler framework, and move on. A confident rationale for an unobservable choice is exactly the overstatement this skill exists to remove.

---

**A. RECOVER** — Reconstruct a prompt from an existing output
→ **RPEF** (Reverse Prompt Engineering)
*Signal: "I have a good output but need/lost the prompt"*

---

**B. CLARIFY** — Requirements are unclear; gather information first

| Signal | Framework |
|--------|-----------|
| Requirements are vague; conduct structured interview | **Reverse Role Prompting** (AI-Led Interview) |
| High-stakes precision, dynamic exemplar retrieval, choice-shuffle ensembling | **Medprompt / Dynamic Few-Shot Ensembling** |

*Reverse Role = requirements discovery through back-and-forth dialogue. Medprompt = precision grounding using semantically retrieved exemplars and permutation ensembling.*

---

**C. CREATE** — Generating new content from scratch

| Signal | Framework |
|--------|-----------|
| Ultra-minimal, one-off | **APE** |
| Simple, expertise-driven | **RTF** |
| Simple, context/situation-driven | **CTF** |
| Role + context + explicit outcome needed | **RACE** |
| Multiple output variants needed | **CRISPE** |
| Business deliverable with KPIs | **BROKE** |
| Explicit rules/compliance constraints | **CARE** or **TIDD-EC** |
| Audience, tone, style are critical | **CO-STAR** |
| Multi-step procedure or methodology | **RISEN** |
| Data transformation (input → output) | **RISE-IE** |
| Content creation with reference examples | **RISE-IX** |
| Non-linear multi-branch problem, DAG topology, combining and refining alternative architectures | **Graph-of-Thoughts (GoT)** |

*TIDD-EC vs. CARE: separate Do/Don't lists → TIDD-EC; combined rules + examples → CARE. Linear methodology → RISEN; non-linear DAG synthesis → Graph-of-Thoughts.*

---

**D. TRANSFORM** — Improving or converting existing content

| Signal | Framework |
|--------|-----------|
| Rewrite, refactor, convert | **BAB** |
| Iterative quality improvement | **Self-Refine** |
| Summarize at fixed length, maximize information | **Chain of Density** |
| Shorten text toward a target length | **Iterative Compression** |
| Outline-first then expand sections | **Skeleton of Thought** |
| Repeated/templated reasoning pattern, retrieve and instantiate distilled thought-template from meta-buffer | **Buffer-of-Thoughts (BoT)** |

---

**E. REASON** — Solving a reasoning, calculation, or architectural problem

| Signal | Framework |
|--------|-----------|
| Numerical/calculation, zero-shot | **Plan-and-Solve (PS+)** |
| Multi-hop with ordered dependencies | **Least-to-Most** |
| Needs first-principles before answering | **Step-Back** |
| Multiple distinct approaches to compare | **Tree of Thought** |
| Verify reasoning didn't overlook conditions | **RCoT** |
| Linear step-by-step reasoning | **Chain of Thought** |
| Answer must be robust; sample many paths and majority-vote | **Self-Consistency** |
| Non-linear dependencies, DAG aggregation & iterative refinement | **Graph-of-Thoughts (GoT)** |
| Multi-expert role coordination across fresh isolated specialist agents via Conductor | **Meta-Prompting** |
| Structural algorithmic archetype matching with instantiated thought-templates | **Buffer-of-Thoughts (BoT)** |
| High-stakes precision, dynamic exemplar retrieval, choice-shuffle ensembling | **Medprompt** |

*Reasoning Framework Discrimination: Chain-of-Thought (linear single-path) vs. Tree-of-Thought (branching search without path recombination) vs. Graph-of-Thoughts (arbitrary DAG with thought aggregation and refinement loops) vs. Buffer-of-Thoughts (template retrieval from meta-buffer to avoid ad-hoc search) vs. Meta-Prompting (multi-expert orchestration across isolated clean contexts) vs. Medprompt (dynamic k-NN exemplar retrieval + CoT + choice shuffling).*

---

**F. CRITIQUE** — Stress-testing, attacking, or verifying output

| Signal | Framework |
|--------|-----------|
| General quality improvement | **Self-Refine** |
| Align to explicit principle/standard | **CAI Critique-Revise** |
| Find the strongest opposing argument | **Devil's Advocate** |
| Identify failure modes before they happen | **Pre-Mortem** |
| Verify reasoning didn't miss conditions | **RCoT** |
| Draft may contain hallucinated facts; verify each claim | **Chain-of-Verification** |

*Self-Refine = any quality. CAI = compliance with an **explicitly stated** standard or requirement set. Devil's Advocate = opposing arguments. Pre-Mortem = failure analysis. RCoT = implicit condition reconstruction. Chain-of-Verification = independent fact-checking of factual claims.*

---

**G. AGENTIC** — Tool-use with iterative reasoning or multi-expert orchestration

| Signal | Framework |
|--------|-----------|
| Task requires tools; each result informs the next step | **ReAct** (Reasoning + Acting) |
| Orchestrate multi-step task across fresh isolated specialist agents via a central Conductor | **Meta-Prompting** |

*ReAct = single-agent interleaved reasoning and tool calls. Meta-Prompting = central Conductor decomposing into decoupled subtasks dispatched to isolated fresh-context expert agents.*

---

#### Combining Frameworks

Most prompts need exactly one framework. Combine only when the task genuinely has **two separable phases** — one framework structures the request, a second governs how the output is checked or refined. If you cannot name the two phases, do not combine.

| When | Combination | Why |
|---|---|---|
| High-stakes content that must survive review | **CO-STAR + Self-Refine** | CO-STAR fixes audience/tone/format; Self-Refine adds a critique-and-revise loop before delivery |
| Multi-step procedure executed with tools | **RISEN + ReAct** | RISEN specifies the steps and success criteria; ReAct governs the tool-use cycle within each step |
| Business deliverable with a hostile audience | **BROKE + Devil's Advocate** | BROKE sets objective and key results; Devil's Advocate stress-tests them before they reach a stakeholder |
| Complex system with multi-agent verification | **Meta-Prompting + GoT** | Meta-Prompting isolates domain specialists; GoT aggregates and refines their sub-architectures |

When you combine, load `assets/templates/hybrid_template.txt` and state plainly in your analysis which framework owns which phase. Never stack more than two.

#### Composable Techniques

Some techniques are layers added *on top of* whichever framework you picked:

- **Few-shot / in-context examples** — showing 2–5 worked input→output examples inside the emitted prompt. Highest-leverage technique in prompting. Insert before the final instruction, in the exact target output format. Never invent examples the user or their material did not supply.
- **Sandwich Prompt Architecture** — Structuring prompts with Head (10% primacy anchor: invariants/schemas), Body (80% passive context: stubs/data), and Tail (10% recency anchor: execution triggers/reminders) to eliminate Lost-in-the-Middle context degradation.
- **Contrastive Positive Steering** — Replacing naive negative prohibitions ("don't", "never") with explicit positive bounded targets to prevent associative token priming ("pink elephant" effect).

---

### 3. Framework Quick Reference

One-line per framework (load `references/frameworks/` for full detail):

**Simple:** APE | RTF | CTF  
**Medium:** RACE | CARE | BAB | BROKE | CRISPE  
**Comprehensive:** CO-STAR | RISEN | TIDD-EC  
**Data:** RISE-IE | RISE-IX  
**Reasoning:** Plan-and-Solve | Chain of Thought | Least-to-Most | Step-Back | Tree of Thought | RCoT | Self-Consistency | Graph-of-Thoughts | Buffer-of-Thoughts | Medprompt  
**Structure/Iteration:** Skeleton of Thought | Chain of Density | Iterative Compression  
**Critique/Quality:** Self-Refine | CAI Critique-Revise | Devil's Advocate | Pre-Mortem | Chain-of-Verification  
**Meta/Reverse:** RPEF | Reverse Role Prompting  
**Agentic / Orchestration:** ReAct | Meta-Prompting  

**Composable techniques:** Few-shot examples | Sandwich Architecture | Contrastive Positive Steering

### 4. Clarification & Probing Questions

Ask targeted questions (3-5 at a time) based on identified gaps. 
* **Interactive Tool Probing**: When running in Antigravity (`agy`), use the `ask_question` tool with structured options or write-in prompts instead of plain unstructured chat text. In Claude Code, use `AskFollowupQuestion`.

**For CO-STAR**: Provide the material this is built from if any, the situation and constraints behind it, who the audience is and what you want them to do, the tone and style to write in, the output format and length?
**For RISEN**: Provide the material the procedure runs on if any, the expertise and methodology to adopt, the steps in order, what must be true when it is done, what is out of scope or must not happen?
**For RISE-IE**: Provide the actual data to be processed (not a description of it), its format and any quirks to expect, the expertise needed, the processing steps in order, what the output must look like?
**For RISE-IX**: The expertise to embody, what to create and its core requirements, the workflow steps, provide 2-3 actual samples whose style and format the output should match?
**For TIDD-EC**: Provide the material this task operates on (the message, document, or dataset itself, not a description of it), what kind of task this is and the background that shapes it, the exact steps in order, what must always be included and what must never happen (state each as a prohibition, not a topic), examples of a good result?
**For CTF**: Provide the artifact this operates on if you have one, the situation and background around it, the exact task and deliverable, the output format?
**For RTF**: Provide the material the task applies to if any, the expertise needed, the exact task and deliverable, the output format and length?
**For APE**: Provide the material the action applies to if any, the one action to perform, why it is needed and who uses the result, what a good result looks like?
**For BAB**: Provide the actual artifact being transformed, what is wrong with it now, what it should become, what rules govern the transformation?
**For RACE**: Provide the material the task applies to if any, the role and expertise needed, the action to perform, the situational context and audience, what a successful output looks like?
**For CRISPE**: The expertise and role to embody, provide the data or style sample it should work from, the background it needs, the exact task and deliverable, the tone and how many variants?
**For BROKE**: Provide the supporting material or performance data if you have it, the current situation and why this task exists, the role to embody, the specific deliverable and the structure and length the response should have, the measurable business outcome it should move?
**For CARE**: Provide the source document or draft this works from if any, your situation and why this task exists, the specific ask and deliverable, what must be included and what would make this output wrong or unusable, an example of what good looks like?
**For Tree of Thought**: The decision or problem and its constraints, provide the evidence the branches must be judged against, the 2-5 distinct approaches to compare, the criteria that decide between them?
**For Graph-of-Thoughts (GoT)**: Does your task involve parallel alternative designs that must be combined and iteratively patched rather than explored down an isolated path? What are the independent candidate branches, what is the scoring function or threshold for acceptable nodes, and what is the aggregation logic?
**For Meta-Prompting**: Does your task require multiple distinct domain specialists (e.g. architect + implementer + security auditor) working in isolated clean contexts? What is the central task directive, what are the discrete sub-tasks, and how should the Conductor synthesize their findings?
**For Buffer-of-Thoughts (BoT)**: Does this problem fit a known algorithmic or structural archetype (divide-and-conquer, dynamic programming, state machine, two-pointer) that should instantiate a proven template? What are the state space parameters, transition rules, and termination boundaries?
**For Medprompt**: Does this high-stakes decision require retrieving semantically similar exemplars and ensembling across shuffled option permutations to eliminate positional/label bias? What is the exemplar bank, what are the active candidate choices, and what consensus voting threshold should be applied?
**For ReAct**: Does the environment this runs in actually have callable tools — if not, stop and use Chain of Thought instead, which tools are available and how each is invoked, what end state counts as success, what limits apply and when to stop?
**For Skeleton of Thought**: The topic or question to outline, provide the document, data, or notes the answer must be drawn from if you have any, who the answer is for and what scope it should cover, how far each point should be expanded (a few sentences, a paragraph, full detail)?
**For Step-Back**: The specific question you want answered, provide the code, document, or design it is about if any, what higher-level principle or concept governs it?
**For Least-to-Most**: The full problem in one statement, provide the material the subproblems must reason over, what is the simplest thing that must be answered first, what does the final answer depend on?
**For Plan-and-Solve**: The problem with every number, unit, and constraint written out, provide the dataset or figures the calculation runs on if any, which values are given and which must be derived?
**For Chain of Thought**: The problem with all its conditions stated, provide the code, data, or document to reason over if any, what the reasoning steps should be?
**For Self-Consistency**: The problem with all its conditions stated, provide the data or figures it runs on if any, what the single final answer should look like so every sampled run ends in a comparable `FINAL ANSWER:` line, how many samples to run and majority-vote over (the paper uses 40; 5-10 is usually enough)?
**For Chain of Density**: Provide the full document to summarize, the fixed word budget every summary must hit, how many densification passes (the paper uses 5)?
**For Iterative Compression**: Provide the content to compress, where it should end up (word count, reading level, single paragraph), what should improve on each pass, how many passes and when to stop?
**For Self-Refine**: Provide the actual draft to improve, which dimensions the critique should cover (clarity, completeness, tone), what would make this output wrong or unusable?
**For CAI Critique-Revise**: Provide the actual output to be critiqued, the specific standard it must satisfy stated precisely enough to be checkable, what would make this output wrong or unusable?
**For Devil's Advocate**: The position, plan, or decision to attack, provide the proposal or memo that sets it out if you have one, which dimensions the attack should cover?
**For Pre-Mortem**: The project or decision being analyzed with its team, timeline, and goals, provide the plan or proposal document if you have one, how far in the future the imagined failure should be dated?
**For RCoT**: The question with every condition and constraint written out, provide the document those conditions come from if any, any implicit requirement not yet written into the question (units, deadlines, exclusions, edge cases) that a correct answer must still satisfy?
**For Chain-of-Verification**: Provide the draft answer to fact-check if you have one, or the factual question to answer carefully, which specific claims are most at risk of being wrong, what a correct final answer must not get wrong?
**For RPEF**: Provide the actual output sample to reverse-engineer, provide the input that produced it or confirm it is output-only, which details are one-off specifics that should become [PLACEHOLDER] variables?
**For Reverse Role**: What you want to achieve in one or two sentences, the domain of expertise to consult, questions one at a time or all at once, should it then do the task or synthesize a structured prompt for you to approve?

### 5. Apply Framework & Ingest Template

Using gathered information:
1. **Load Template Explicitly**: Call file reading tool (`view_file`) on `assets/templates/<framework>_template.txt` to read the exact template structure into context.
2. Map user's information to framework components.
3. Fill missing elements with reasonable defaults — **with two exceptions, below**.
4. Structure according to framework format.
5. **Decide whether worked examples would materially improve the output**; if so, load `references/techniques/few-shot.md` and layer in few-shot examples. Reach for it especially on classification, extraction, strict-format, and style-matching tasks, and only when the user or their material supplies real examples.

**Never default a fact about the user's world.** Where such a slot is unanswered, emit a visible `[you fill this in: <what is needed>]` placeholder and list every placeholder in your analysis section.

**Never soften or drop a prohibition.** If the user said something must not happen, translate it using Contrastive Positive Steering into an explicit, bounded requirement.

### 6. Present Improvements & File Persistence

Structure your output in this exact order:

**A. Analysis section** (comes first):
- Framework selected and why
- Changes made and reasoning
- Framework components applied

**B. Usage instructions** (transition block, immediately before the prompt):

> **Your revised prompt is ready.**
> - **New chat**: Copy the prompt below and paste it as your first message in a new conversation.
> - **Same chat**: Tell the assistant: *"Use the revised prompt you just provided as a new instruction and execute it."*

**C. The revised prompt** (comes last, in a fenced code block):
- Present as a clean, flat-text block inside triple backticks.
- **No framework section headers** (no "BEFORE:", "BRIDGE:", "CONTEXT:", etc.) — these are scaffolding, not part of the deliverable.
- **No indentation** beyond what the prompt itself genuinely requires.
- **No markdown formatting** inside the block unless the prompt explicitly needs it (e.g., it asks for tables).
- The user must be able to copy the entire block contents and paste it verbatim with zero editing — except for `[...]` placeholders.
- **Nothing after the code block** — the revised prompt must be the absolute last element in the chat response.

**D. Direct File Persistence (Harness Action)**:
- If the user requested saving the prompt to a file (e.g. `.agents/prompts/name.txt`, `.agents/rules/name.md`, or a project file), use `write_to_file` to write the clean prompt directly to disk.

### 7. Iterate & Verify

- Confirm improvements align with intent.
- Refine based on feedback.
- **Empirical Verification (Subagent Benchmarking)**: When validating a mission-critical or complex prompt, use `invoke_subagent` to test-run both the original prompt and revised prompt against a sample task to benchmark response quality and compliance.

---

## Detailed Framework Profiles: SOTA Reasoning Paradigms

### Graph-of-Thoughts (GoT)

- **Foundational Citation:** Besta et al., ETH Zürich (AAAI 2024), [arXiv:2308.09687](https://arxiv.org/abs/2308.09687)
- **Primary Intent Signal:** Non-linear multi-branch problem, DAG topology, combining and refining alternative architectures.
- **Discriminating Contrast:**
  - *Chain-of-Thought (CoT)* is strictly linear: $T_1 \rightarrow T_2 \rightarrow T_3$.
  - *Tree-of-Thoughts (ToT)* branches into isolated search paths without recombination ($T_0 \rightarrow \{T_{1a}, T_{1b}\}$).
  - *Graph-of-Thoughts (GoT)* models thought spaces as an arbitrary directed acyclic graph $G = (V, E)$, enabling multiple distinct thought branches to merge via `Aggregate` and iterate via `Refine`.
- **Algorithmic Operators:**
  1. `Generate(t)`: Produces $k$ successor thoughts from an existing thought node $t$.
  2. `Aggregate(t_1, t_2, ...)`: Synergistically synthesizes multiple disparate thoughts into a unified composite thought.
  3. `Refine(t)`: Executes an in-place feedback iteration on an existing thought based on diagnostic evaluation.
  4. `Score(t) -> s`: Computes a scalar quality score $s \in [0, 1]$ evaluating node utility against stated constraints.
- **Step-by-Step Execution Protocol:**
  1. **Node Decomposition**: Partition the core problem into $M$ independent structural dimensions or sub-problems.
  2. **Parallel Generation**: For each dimension, generate candidate partial thoughts in parallel.
  3. **Synergistic Aggregation**: Execute `Aggregate`, synthesizing combinations of partial candidates into integrated full architectures.
  4. **Graph Evaluation**: Score each integrated thought using an objective constraint-satisfaction function.
  5. **Loop Refinement**: If top scores fall below threshold $\tau$, route the highest-ranking candidate through `Refine` using error diagnostics until convergence.

#### GoT Prompt Template

```markdown
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

---

### Meta-Prompting

- **Foundational Citation:** Suzgun & Kalai, Harvard University & Microsoft Research (2024), [arXiv:2401.12954](https://arxiv.org/abs/2401.12954)
- **Primary Intent Signal:** Orchestrate multi-step task across fresh isolated specialist agents via a central Conductor.
- **Discriminating Contrast:**
  - *Standard Multi-Persona Prompting* simulates dialogue between personas within a single context window, inducing context pollution, role confusion, and mutual reinforcement of hallucinations.
  - *Meta-Prompting* establishes an authoritative top-level Conductor that decomposes the task, dynamically spawns specialized expert queries executed in *fresh, isolated contexts*, and critically audits and synthesizes their independent returns.
- **Algorithmic Mechanics:**
  1. **Task Analysis & Decomposition**: The Conductor breaks the prompt into independent domain sub-queries.
  2. **Fresh-Context Expert Allocation**: Each sub-query is dispatched with an optimal specialized role persona in a zero-state context.
  3. **Execution & Tool Verification**: Sub-agents evaluate their isolated tasks.
  4. **Synthesis & Sanity Audit**: The Conductor inspects sub-answers, checks for mutual consistency and boundary compliance, and synthesizes the final response.

#### Meta-Prompting Template

```markdown
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

---

### Buffer-of-Thoughts (BoT)

- **Foundational Citation:** Yang et al., Peking University & UC Berkeley (NeurIPS 2024 Spotlight), [arXiv:2406.04271](https://arxiv.org/abs/2406.04271)
- **Primary Intent Signal:** Repeated/templated reasoning pattern, retrieve and instantiate distilled thought-template from meta-buffer.
- **Discriminating Contrast:**
  - *Tree-of-Thoughts* performs combinatorial search from scratch on every run, resulting in high latency and cost.
  - *Buffer-of-Thoughts* retrieves a pre-distilled, high-level **thought-template** from a persistent meta-buffer and instantiates it with problem-specific parameters, reducing latency and cost to **12% of ToT/GoT** while boosting accuracy.
- **Core Architectural Components:**
  1. **Meta-Buffer**: Persistent repository of abstracted thought-templates categorized by algorithmic and architectural archetypes.
  2. **Thought-Retriever**: Semantic selection mechanism matching problem constraints to the optimal template.
  3. **Thought-Instantiator**: Parameterizes the abstract template with concrete problem variables and constraints.
  4. **Buffer-Manager**: Continuously extracts and distills novel structural templates from successful runs.

#### BoT Prompt Template

```markdown
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

---

### Medprompt / Dynamic Few-Shot Ensembling

- **Foundational Citation:** Nori et al., Microsoft Research (2023), [arXiv:2311.16452](https://arxiv.org/abs/2311.16452)
- **Primary Intent Signal:** High-stakes precision, dynamic exemplar retrieval, choice-shuffle ensembling.
- **Discriminating Contrast:**
  - Standard Few-Shot prompting uses static, hand-written exemplars that may be semantically distant from the test query and suffer from recency/order bias.
  - Medprompt combines three composable techniques: (1) Dynamic $k$-NN exemplar retrieval based on query embeddings, (2) Self-generated CoT reasoning on exemplars, and (3) Choice-shuffle ensembling across $N$ permutations to neutralize label bias.
- **Algorithmic Triad:**
  1. **Dynamic $k$-NN Retrieval**: Selects the $k$ most semantically relevant exemplars from a trusted offline bank.
  2. **Self-Generated CoT**: Generates step-by-step reasoning paths for each exemplar using the foundation model itself.
  3. **Choice-Shuffle Ensembling**: Systematically permutes the candidate order across multiple inferences, aggregating predictions via plurality voting to neutralize positional and label token priors.

#### Medprompt Prompt Template

```markdown
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

---

## Web Codebase Prompt Engineering Guide

When engineering prompts for modern web codebases (Next.js App Router, React, TypeScript, Tailwind CSS), naive context injection leads to token exhaustion, hallucinated state coupling, and broken accessibility. Follow these production engineering practices.

### 1. The 3-Stage Hierarchical Prompting Pipeline

Autonomous agents with unconstrained terminal and file access suffer from severe trajectory divergence and extreme monetary costs (\$5–\$20+ per issue). Standardize prompts on a deterministic 3-stage pipeline (Agentless / RepoCoder):

1. **Stage 1: Hierarchical Localization**:
   - *File Ranking*: Given only the repository file tree and feature/issue spec, identify the 1–3 candidate files responsible.
   - *Skeleton Localization*: Strip function bodies and inspect only class, function, and interface signatures to locate target entities.
   - *Span Localization*: Select the exact line range or AST block requiring modification.
2. **Stage 2: Context Slicing**:
   - Extract only imported type definitions, route contracts, and utility signatures directly related to the localized span.
   - Filter out all internal presentation markup, SVG paths, and decorative styles from caller contexts.
3. **Stage 3: Targeted Generation & Verification**:
   - Emit surgical diff patches targeting strictly the identified span.
   - Validate immediately with AST syntax parsing and regression tests.

### 2. Component Interface Stubs vs. AST Context Dumping

Injecting full React component files into prompt contexts introduces 2,500–6,000 tokens of presentation noise (Tailwind classes, SVG paths, local hooks) per file, triggering the Lost-in-the-Middle effect and causing models to manipulate private child state.

Instead, extract and inject **Component Interface Stubs** (`.d.ts` representations):

```typescript
// Sliced Component Interface Stub (~18 lines, 120 tokens vs 450 lines raw JSX)
export interface UserProfileData {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'member' | 'guest';
  avatarUrl: string | null;
}

export interface UserProfileCardProps {
  userId: string;
  initialData: UserProfileData;
  onSave: (updated: Partial<UserProfileData>) => Promise<{ success: boolean; error?: string }>;
}

export declare function UserProfileCard(props: UserProfileCardProps): React.JSX.Element;
```

**Result**: 96% token reduction with 100% typing fidelity, preserving critical attention capacity for generation logic.

### 3. Execution Boundary Invariants (Full-Stack Runtimes)

Modern full-stack frameworks execute across distinct environments with incompatible capabilities. Web prompts must explicitly declare and enforce execution boundaries:

1. **Server Components (`RSC` - Default)**:
   - May access database drivers (`db`, `prisma`), filesystem (`node:fs`), and private environment variables (`process.env.SECRET_*`).
   - Prohibited from declaring client state (`useState`, `useReducer`), client hooks (`useEffect`), and event listeners (`onClick`, `onChange`).
2. **Client Components (`'use client'`)**:
   - Executed during server pre-rendering and hydrated in the browser DOM.
   - May register event listeners, maintain local UI state, and access browser APIs (`window`, `localStorage`).
   - Strictly prohibited from importing database clients, private secrets, or server-only utilities.
3. **Server Actions (`'use server'`)**:
   - Publicly exposed HTTP RPC endpoints.
   - Must treat all incoming arguments as untrusted user input, enforcing runtime validation schemas (Zod).

#### Boundary Contract Specification Block

```markdown
### BOUNDARY CONTRACT: [SERVER_COMPONENT | CLIENT_COMPONENT | SERVER_ACTION]

1. Execution Realm:
   - Target Runtime: [Node.js / Edge Server] OR [Browser DOM / Client Hydration]
   - Directive Required: `'use client'` OR `'use server'` OR None (Default Server Component)

2. Boundary Invariants:
   - Permitted Imports:
     - IF SERVER: Database clients (`db`, `prisma`), server-only headers, secrets (`process.env.SECRET_*`).
     - IF CLIENT: UI libraries (`framer-motion`), React client hooks (`useState`, `useCallback`), browser APIs.
   - Prohibited Imports:
     - IF SERVER: Client hooks (`useState`, `useEffect`), DOM event listeners (`onClick`, `onSubmit`).
     - IF CLIENT: Database connections, server-only secret keys, file system modules (`node:fs`).

3. Serialization Boundaries:
   - All props passed across Server-to-Client boundaries MUST be JSON-serializable.
   - Do NOT pass class instances, functions, or unformatted Date objects across boundaries.

4. Input Validation (Server Actions):
   - All server action arguments MUST be treated as untrusted and validated via runtime schema validation (Zod).
```

### 4. Frontend Invariants: Semantic HTML & Accessibility (WCAG 2.2 AA)

Over 96.8% of top web pages suffer accessibility violations from LLM-generated "div soup". Enforce four mandatory frontend invariants:

1. **"Semantic HTML First" (Anti-Div-Soup)**:
   - Layouts must declare semantic landmark regions: `<header>`, `<nav>`, `<main>`, `<aside>`, `<footer>`.
   - Actions triggering state changes must use `<button type="button|submit">`, never `<div onClick={...}>` or `<a onClick={...}>`.
   - Navigation actions must use `<a href="...">` or framework `<Link href="...">`.
   - Form inputs must be linked to `<label htmlFor="id">`. Grouped inputs must use `<fieldset>` with `<legend>`.
2. **Keyboard Operability & Focus Management**:
   - All interactive controls must be navigable via `Tab` in logical visual order.
   - Modals and slide-over drawers must implement **focus trapping**: move focus into modal on open, wrap focus cyclically, close and return focus to trigger on `Escape`.
   - Positive `tabindex` attributes (`tabindex="1"`) are strictly forbidden. Use `tabindex="0"` for custom interactive elements and `tabindex="-1"` for programmatic focus.
   - Visible focus rings must be styled via `:focus-visible` (e.g. `focus-visible:ring-2 focus-visible:ring-offset-2`). Banning `outline: none` without a visible focus replacement.
3. **WAI-ARIA 1.2 State Reflection**:
   - Expandable/collapsible controls must dynamically synchronize `aria-expanded="true|false"` on the trigger and `aria-controls="panel-id"` on the controlled container.
   - Modal dialogs must declare `role="dialog"`, `aria-modal="true"`, and `aria-labelledby="dialog-title-id"`.
   - Standalone icon buttons must declare an accessible name via `aria-label` or visually hidden text (`sr-only`). Decorative icons must declare `aria-hidden="true"`.
4. **Visual Contrast & Reduced Motion**:
   - Body text must achieve a minimum **4.5:1** contrast ratio against its background. Large text (≥18pt or ≥14pt bold) and active UI boundaries must achieve **3:1**.
   - Transitions and animations must respect user preferences via `@media (prefers-reduced-motion: reduce)` / `motion-reduce:transition-none`.

### 5. Defensive Web Security (OWASP Top 10 for LLMs)

1. **Client Bundle Secret Isolation (OWASP LLM06 / CWE-200)**:
   - Components marked `'use client'` must NEVER reference private environment variables (`DATABASE_URL`, `API_KEY`, `JWT_SECRET`).
   - Only variables prefixed with `NEXT_PUBLIC_` or `VITE_` may appear in client bundles.
   - Data access modules must include `import 'server-only'` to cause compile-time build failures if leaked into client bundles.
2. **Runtime Schema Validation on All External Inputs (OWASP LLM02 / CWE-20)**:
   - Every API route handler, webhook receiver, and Server Action must validate incoming payloads using strict Zod schemas (`schema.safeParse()`).
   - Unvalidated form data or request bodies must never be passed directly into ORM mutations.
3. **IDOR Prevention & Session Identity Scoping (CWE-284)**:
   - Never trust client-supplied `userId` or `tenantId` in mutations.
   - Extract authenticated identity strictly from the verified server session:
     `where: { id: input.postId, authorId: session.user.id }`.
4. **XSS Mitigation & Safe Output Sanitization (CWE-79)**:
   - `dangerouslySetInnerHTML`, `v-html`, and `{@html}` are strictly forbidden unless sanitized via `DOMPurify.sanitize()`.
   - Dynamic URLs in anchor links (`<a href={url}>`) must validate protocols against an explicit whitelist (`https:`, `mailto:`, `tel:`), explicitly banning `javascript:` pseudo-protocols.

---

## Framework References

Detailed framework docs in `references/frameworks/`:
- `co-star.md` - Context, Objective, Style, Tone, Audience, Response
- `risen.md` - Role, Instructions, Steps, End goal, Narrowing
- `rise.md` - Dual variant support: RISE-IE (Input-Expectation) & RISE-IX (Instructions-Examples)
- `tidd-ec.md` - Task type, Instructions, Do, Don't, Examples, Context
- `ctf.md` - Context, Task, Format
- `rtf.md` - Role, Task, Format
- `ape.md` - Action, Purpose, Expectation (ultra-minimal)
- `bab.md` - Before, After, Bridge (transformation/rewrite tasks)
- `race.md` - Role, Action, Context, Expectation (medium complexity)
- `crispe.md` - Capacity+Role, Insight, Instructions, Personality, Experiment
- `broke.md` - Background, Role, Objective, Key Results, Evolve
- `care.md` - Context, Ask, Rules, Examples (constraint-driven)
- `tree-of-thought.md` - Branching exploration of multiple solution paths
- `got.md` - Graph-of-Thoughts: arbitrary DAG reasoning with aggregation and refinement
- `meta-prompting.md` - Task-agnostic conductor orchestrating fresh-context expert instances
- `bot.md` - Buffer-of-Thoughts: thought-template retrieval and parameter instantiation
- `medprompt.md` - Dynamic few-shot k-NN retrieval, self-generated CoT, choice-shuffle ensembling
- `react.md` - Reasoning + Acting (agentic tool-use cycles)
- `skeleton-of-thought.md` - Skeleton-first then expand (parallel generation)
- `step-back.md` - Abstract to principles first, then answer (Google DeepMind)
- `least-to-most.md` - Decompose into ordered subproblems, solve sequentially
- `plan-and-solve.md` - Zero-shot: plan + extract variables + calculate (PS+)
- `chain-of-thought.md` - Step-by-step reasoning techniques
- `chain-of-density.md` - Entity densification at fixed length, for summarization (Adams et al.)
- `iterative-compression.md` - Progressive shortening toward a target length
- `self-refine.md` - Generate → Feedback → Refine loop (NeurIPS 2023)
- `cai-critique-revise.md` - Principle-based critique + revision (Anthropic)
- `devils-advocate.md` - Strongest opposing argument generation (ACM IUI 2024)
- `pre-mortem.md` - Assume failure, identify causes + warning signs (Gary Klein)
- `rcot.md` - Reverse Chain-of-Thought: verify by reconstructing the question
- `rpef.md` - Reverse Prompt Engineering: recover prompt from output (EMNLP 2025)
- `reverse-role.md` - AI-Led Interview: AI asks you questions first (FATA)
- `self-consistency.md` - Sample N reasoning paths, majority-vote externally (Wang et al., ICLR 2023)
- `chain-of-verification.md` - Draft, plan checks, verify independently, revise (Dhuliawala et al., Findings of ACL 2024)

Load these when applying specific frameworks for detailed component guidance, selection criteria, and examples.

**Composable techniques** live in `references/techniques/`:
- `few-shot.md` - In-context examples: when to add them, how many, ordering, label-space rules

**Harness tool adaptations** live in `references/harnesses/`:
- `antigravity.md` - Antigravity CLI (`agy`) tool mappings
- `claude-code.md` - Claude Code tool mappings

## Templates

Every framework has a fill-in template at `assets/templates/<framework>_template.txt`, named after the framework's reference doc (e.g. `co-star.md` → `co-star_template.txt`). RISE has two: `rise-ie_template.txt` and `rise-ix_template.txt`. Additional templates: `hybrid_template.txt` (combined-framework prompts), `got_template.txt`, `meta_prompting_template.txt`, `bot_template.txt`, and `medprompt_template.txt`.

## Key Principles

1. **Ask Before Assuming** - Don't guess intent; clarify ambiguities using interactive tools
2. **Explain Reasoning** - Why this framework? Why these changes?
3. **Show Your Work** - Display analysis, show framework mapping
4. **Be Iterative** - Start with analysis, refine progressively
5. **Respect User Choices** - Adapt if user prefers different framework
6. **Leverage Harness Tools** - Ingest files, read templates via file viewer, probe interactively, persist directly to disk
7. **Enforce Attention & Cognitive Dynamics** - Apply Sandwich Prompt structuring and Contrastive Positive Steering to prevent context sink degradation and associative priming errors

## When NOT to Use Frameworks

Frameworks add structure — but structure has overhead. Skip them when:

- **The prompt is already complete**: Clear goal, full context, defined format → just execute it.
- **Purely factual lookups**: "What is the capital of France?" — no framework needed.
- **Conversational exchanges**: Back-and-forth dialogue doesn't need a structured template.
- **Very short one-off tasks**: "Translate this sentence to Spanish." APE would be overhead; just translate.
- **User is in a hurry**: If someone explicitly says "just do it", don't pause for framework selection — deliver, then offer to structure if they want more.
- **The task is fully specced by context**: When the codebase, existing docs, or prior messages already contain everything needed.

**Rule of thumb**: Apply a framework when there's a gap between what the user *asked for* and what they *need*. If there's no gap, there's no job for a framework.

---

## Example Interaction

This example shows the full intent-based flow — detecting intent, using the discriminating table, selecting a framework, asking questions, and delivering a structured result.

**User**: "Rewrite this job posting in `docs/job-post.md` — it's too formal and isn't getting applicants."

**Assistant**: 
1. Reads `docs/job-post.md` via `view_file`.
2. Assesses initial score (Clarity: 6, Specificity: 4, Context: 5, Completeness: 5, Structure: 5, Attention & Cognitive Dynamics: 4 → Overall: 4.8).
3. Detects intent: **TRANSFORM** → **BAB** (Before, After, Bridge).
4. Loads `assets/templates/bab_template.txt` via `view_file`.
5. Clarifies requirements with structured questions via `ask_question`.

**Analysis (BAB framework applied)**:
1. Locked the current state so the AI understands the starting point
2. Defined the target state in terms the AI can evaluate against
3. Made transformation rules explicit and prioritized using contrastive positive steering
4. Protected non-negotiable elements (requirements) from being changed
5. Structured with Head and Tail anchors to eliminate context sink degradation
6. Gave a concrete length/tone constraint to prevent over-engineering

> **Your revised prompt is ready.**
> - **New chat**: Copy the prompt below and paste it as your first message in a new conversation.
> - **Same chat**: Tell the assistant: *"Use the revised prompt you just provided as a new instruction and execute it."*

```
[Paste the current job posting here]

The job posting above suffers from corporate-speak, passive voice, overly formal tone, and generic language that doesn't reflect actual team culture.

The rewritten version should sound like it was written by engineers, for engineers. Early-career developers should read it and think "I want to work there." It should feel honest, direct, and human — not like legal boilerplate.

Follow these rules:
- Replace all passive constructions with active voice.
- Convert corporate jargon to plain English (e.g., "leverage" → "use").
- Add one specific, concrete detail about the team or culture per section.
- Keep all technical requirements and must-haves verbatim — do not change these.
- Target reading level: conversational, not academic.
- Length: same or shorter than the original. Cut fluff, don't add it.

Now rewrite the job posting above.
```

---

## Usage Notes

- Ingest source files directly using `view_file` or search codebase with `grep_search`
- Always analyze the original prompt with the 6-dimension rubric including Attention & Cognitive Dynamics
- Recommend framework(s) with reasoning
- Load framework template explicitly via `view_file` from `assets/templates/`
- Ask clarifying questions progressively using interactive questioning tools (`ask_question` / `AskFollowupQuestion`)
- Present improvements cleanly without scaffolding headers
- Offer to save to file (`write_to_file`) or run subagent benchmark (`invoke_subagent`) when appropriate
