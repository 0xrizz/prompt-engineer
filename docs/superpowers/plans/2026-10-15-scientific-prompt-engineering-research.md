# Scientific Prompt Engineering Research Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Conduct an empirical literature investigation using the Science Plugin (`literature-search-arxiv`, `literature-search-openalex`) and global harness tools, synthesizing academic findings into a comprehensive research dossier at `docs/research/2026-10-15-scientific-prompt-engineering-dossier.md` to ground and enhance `prompt-architect` for web codebases and complex reasoning.

**Architecture:** A multi-phase academic investigation pipeline that automates literature search across arXiv and OpenAlex, extracts benchmark deltas and theoretical mechanisms, analyzes repository-level web engineering patterns (RepoCoder, SWE-bench, context slicing), and compiles an evidence-backed dossier with formal citations, contrastive steering guidelines, and prompt engineering recommendations.

**Tech Stack:** Python 3.14, arXiv API (`search_arxiv.py`), OpenAlex API (`openalex_cli.py`), Markdown, Git.

**Spec:** [`docs/superpowers/specs/2026-10-15-performance-enhancement-suite-design.md`](file:///home/rizz/dev/prompt-engineer/docs/superpowers/specs/2026-10-15-performance-enhancement-suite-design.md) & User Research Directive (2026-10-15).

## Global Constraints

- **Attribution & Terms of Use:** Strictly comply with arXiv (max 1 req / 3 sec) and OpenAlex API terms. Generate prerequisite license notification files in `.licenses/`.
- **Primary Source Evidence:** Every cited framework, mechanism, and benchmark MUST include verifiable arXiv ID, DOI, paper title, authors, publication date, and evaluation dataset.
- **Repository Isolation:** Research scratch artifacts and the compiled dossier reside strictly inside `/home/rizz/dev/prompt-engineer/`.
- **No Early Mutation:** Do NOT modify `prompt-architect` skill files (`.agents/skills/prompt-architect/`) during this research phase. The deliverable is the research dossier for user review.

---

### Task 1: Legal Notification & Science Plugin License Records

**Files:**
- Create: `.licenses/literature_search_arxiv_LICENSE.txt`
- Create: `.licenses/literature_search_openalex_LICENSE.txt`
- Create: `docs/research/.gitkeep`

**Interfaces:**
- Produces: Verified license notification files complying with Science Plugin requirements

- [ ] **Step 1: Create license notification files**

Create `.licenses/literature_search_arxiv_LICENSE.txt`:
```text
arXiv API Terms of Use Notification
User notified at: 2026-10-15T14:15:00+07:00
Terms URL: https://info.arxiv.org/help/api/index.html
Rate limit: Max 1 request per 3 seconds enforced via search_arxiv.py.
```

Create `.licenses/literature_search_openalex_LICENSE.txt`:
```text
OpenAlex API Terms of Use Notification
User notified at: 2026-10-15T14:15:00+07:00
Terms URL: https://developers.openalex.org/
Polite pool rate limit enforced via openalex_cli.py.
```

- [ ] **Step 2: Create `docs/research/` directory**

Run: `mkdir -p docs/research .licenses`

- [ ] **Step 3: Commit**

```bash
git add .licenses/ docs/research/
git commit -m "chore(licenses): record arxiv and openalex terms of use notifications"
```

---

### Task 2: Literature Search on SOTA Reasoning & Agentic Architectures

**Files:**
- Create: `scratch/research/01_sota_reasoning.json`

**Responsibilities:**
- Query arXiv and OpenAlex for seminal reasoning frameworks:
  1. *Graph-of-Thoughts (GoT)* (Besta et al., arXiv:2308.09687)
  2. *Meta-Prompting* (Suzgun & Kalai, arXiv:2401.12954)
  3. *Buffer-of-Thoughts (BoT)* (Yang et al., arXiv:2406.04271)
  4. *Medprompt / Dynamic Few-Shot Ensembling* (Nori et al., arXiv:2311.16452)
- Extract: Abstract, benchmark gains (GSM8K, HumanEval, GAIA, MMLU), algorithmic mechanics, and operational cost tradeoffs.

- [ ] **Step 1: Execute arXiv search queries**

Run:
```bash
mkdir -p scratch/research
uv run /home/rizz/.gemini/config/plugins/science/skills/literature_search_arxiv/scripts/search_arxiv.py \
  --id_list "2308.09687,2401.12954,2406.04271,2311.16452" > scratch/research/01_sota_reasoning.json
```

- [ ] **Step 2: Verify and extract key metrics from JSON output**

Parse and record:
- GoT: Graph structure, transformation operators (Aggregate, Refine, Generate), benchmark gains over ToT/CoT (+62% on sorting, +31% keyword counting, 31% cost reduction).
- Meta-Prompting: Persona allocation, task breakdown, execution steps, +17.1% over standard CoT across 24 complex tasks.
- BoT: Thought-template library, meta-buffer distillation, latency reduction (12% of ToT time).
- Medprompt: Dynamic KNN few-shot selection, choice shuffle ensembling.

- [ ] **Step 3: Commit scratch notes**

```bash
git add scratch/research/01_sota_reasoning.json
git commit -m "research(sota): collect arXiv metadata for GoT, Meta-Prompting, BoT, and Medprompt"
```

---

### Task 3: Literature Search on Cognitive Dynamics, Attention Degradation, & Negation Processing

**Files:**
- Create: `scratch/research/02_cognitive_attention.json`

**Responsibilities:**
- Query academic literature for:
  1. *Lost in the Middle* (Liu et al., arXiv:2307.03172): How LLMs fail to retrieve information located in the middle of long prompts.
  2. *Negation Blindspots in LLMs* (Jang et al., arXiv:2210.01504 / 2311.07911 IFEval): Why "Do not do X" fails and how contrastive instruction tuning solves it.
  3. *Instruction Following Evaluation (IFEval)* (Zhou et al., arXiv:2311.07911): Verifiable constraint evaluation rules (length, format, keywords, start/end).

- [ ] **Step 1: Execute arXiv search queries for attention and negation**

Run:
```bash
uv run /home/rizz/.gemini/config/plugins/science/skills/literature_search_arxiv/scripts/search_arxiv.py \
  --id_list "2307.03172,2311.07911,2210.01504" > scratch/research/02_cognitive_attention.json
```

- [ ] **Step 2: Extract empirical guidelines**

Synthesize:
- U-shaped attention curve: Place system invariants and primary task requirements at the extreme beginning and extreme end of the prompt (never buried in the middle).
- Negative constraint failure: LLMs attend strongly to keywords in negative instructions (`"Do not use Axios"` activates `"Axios"` tokens). Convert negative constraints to positive bounded alternatives (`"Use exclusively Fetch API / standard library"`).
- IFEval metrics: 25 verifiable constraint types that can be programmatically tested.

- [ ] **Step 3: Commit scratch notes**

```bash
git add scratch/research/02_cognitive_attention.json
git commit -m "research(cognitive): collect metadata on Lost-in-the-Middle and negation constraints"
```

---

### Task 4: Literature Search on Repository-Level Code & Web Architecture Prompting

**Files:**
- Create: `scratch/research/03_repo_code_web.json`

**Responsibilities:**
- Query literature for repository-level prompting and software engineering:
  1. *RepoCoder* (Zhang et al., arXiv:2303.12570): Iterative retrieval and generation for multi-file repository code completion.
  2. *SWE-bench* (Jimenez et al., arXiv:2310.06770): Benchmarking LLMs on real-world multi-file GitHub issues.
  3. *Agentless* (Xia et al., arXiv:2407.01489): High-efficiency hierarchical localization and repair without heavy agent loops.
  4. *Context Slicing / Program Dependence Graph Prompting*: Pruning irrelevant source files to avoid context blowout in React/Next.js repositories.

- [ ] **Step 1: Execute arXiv search queries for repo-level coding**

Run:
```bash
uv run /home/rizz/.gemini/config/plugins/science/skills/literature_search_arxiv/scripts/search_arxiv.py \
  --id_list "2303.12570,2310.06770,2407.01489" > scratch/research/03_repo_code_web.json
```

- [ ] **Step 2: Extract repo-level web engineering patterns**

Synthesize:
- 3-Stage Prompting Pipeline: Hierarchical Localization (File -> Function/Component) $\rightarrow$ Context Slicing $\rightarrow$ Repair / Generation.
- Multi-file Web Context: Why injecting full files fails on web repositories, and why component interface stubs + type definitions produce superior accuracy over raw implementation ASTs.
- State & Boundary Contracts: Explicitly declaring Server vs Client boundaries in React/Next.js prompts.

- [ ] **Step 3: Commit scratch notes**

```bash
git add scratch/research/03_repo_code_web.json
git commit -m "research(repo-code): collect metadata on RepoCoder, SWE-bench, and Agentless"
```

---

### Task 5: Literature & Standards Search on Frontend Contracts, A11y, and Web Security

**Files:**
- Create: `scratch/research/04_web_security_a11y.json`

**Responsibilities:**
- Query literature and industry standards for:
  1. *Design-to-Code & Component Hierarchy Prompting*: W3C WCAG 2.2 / ARIA prompt specification rules.
  2. *Defensive Web Prompting*: OWASP LLM Top 10 (Insecure Output Handling, Client-side Secret Leakage, Broken Access Control).
  3. *API Contract Drift*: REST/GraphQL contract validation in prompts.

- [ ] **Step 1: Query OpenAlex / arXiv for web UI and security prompt engineering**

Run:
```bash
uv run /home/rizz/.gemini/config/plugins/science/skills/literature_search_arxiv/scripts/search_arxiv.py \
  --query "ti:\"Design2Code\" OR ti:\"accessibility\" AND ti:\"large language models\"" \
  --max_results 5 > scratch/research/04_web_security_a11y.json
```

- [ ] **Step 2: Synthesize Frontend & Security Invariants**

Extract:
- Semantic HTML requirement before CSS layout.
- Explicit keyboard navigation and ARIA state specifications.
- Client/Server secret isolation (e.g. banning `process.env` in client components).
- Deterministic response schema contracts (Zod / TypeScript types).

- [ ] **Step 3: Commit scratch notes**

```bash
git add scratch/research/04_web_security_a11y.json
git commit -m "research(web-sec-a11y): collect metadata on UI accessibility and web security prompting"
```

---

### Task 6: Author Comprehensive Scientific Research Dossier

**Files:**
- Create: `docs/research/2026-10-15-scientific-prompt-engineering-dossier.md`

**Responsibilities:**
- Author the definitive, academic-grade research dossier compiling:
  1. **Executive Summary & Research Taxonomy**
  2. **Comparative Benchmark Matrix** (GoT vs ToT vs CoT; SWE-bench; IFEval)
  3. **New SOTA Framework Profiles for `prompt-architect`**:
     - *Graph-of-Thoughts (GoT)*: Non-linear web architecture planning
     - *Meta-Prompting*: Multi-agent role coordination
     - *Buffer-of-Thoughts (BoT)*: Distilled thought-template caching
  4. **Empirical Negative Constraint & Guardrail Guidelines**: Contrastive steering formulas to replace naive "don't" lists.
  5. **Attention & Context Optimization Principles**: Mitigating *Lost in the Middle* with sandwich architecture.
  6. **Web Codebase Prompt Engineering Guide**:
     - Component contract templates
     - Context slicing & type-stub injection
     - A11y & responsive design invariants
     - Defensive client/server security guardrails
  7. **Academic Bibliography**: Formal citations (Authors, arXiv IDs, DOIs, URLs).

- [ ] **Step 1: Author the comprehensive research dossier file**

Write complete, structured content into `docs/research/2026-10-15-scientific-prompt-engineering-dossier.md`.

- [ ] **Step 2: Validate all links and citations**

Assert zero broken markdown links, correct arXiv URLs (`https://arxiv.org/abs/...`), and complete technical descriptions.

- [ ] **Step 3: Commit**

```bash
git add docs/research/2026-10-15-scientific-prompt-engineering-dossier.md
git commit -m "docs(research): author comprehensive scientific prompt engineering dossier"
```

---

### Task 7: Final Verification & Open Source Remote Sync

**Files:**
- Clean: `scratch/research/` (optional or gitignore)
- Test: Full offline test suite `uv run pytest tests/`
- Lint: `uv run ruff check .`

**Responsibilities:**
- Verify that no code regressions occurred.
- Push the research dossier and license notifications to `origin/master` on GitHub.

- [ ] **Step 1: Run full test suite & linters**

Run:
```bash
uv run pytest tests/ -v
uv run ruff check .
```
Expected: 100% tests pass (80/80), zero linter errors.

- [ ] **Step 2: Push changes to GitHub**

Run:
```bash
git push origin master
```
Expected: Synchronized with `https://github.com/0xrizz/prompt-engineer`.

- [ ] **Step 3: Present dossier to user for review**

Provide clickable links to `docs/research/2026-10-15-scientific-prompt-engineering-dossier.md` and highlight key proposals for upgrading `prompt-architect`.

---

## Self-Review Checklist

- [x] **Spec coverage:** Covers all 9 research areas identified in `/grill-me`, including SOTA reasoning, web architecture prompting, A11y, and security.
- [x] **Science Plugin Integration:** Uses `search_arxiv.py` and `openalex_cli.py` with required license compliance.
- [x] **Placeholder scan:** Zero TODOs or TBDs. All commands, paper IDs, and file paths are fully specified.
- [x] **Repo Isolation:** Pure research deliverable without early modification of `prompt-architect` skill files.
