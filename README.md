# 🏛️ Prompt Engineer Hub & Studio

A centralized studio and multi-repo hub to manage, engineer, evaluate, and catalog prompts across all repositories in `/home/rizz/dev/`.

## 🌟 Key Capabilities

- **Automated Repository Profiling**: Detects tech stacks, package managers, test runners, linters, and instruction files (`AGENTS.md`, `CLAUDE.md`) for all projects in `/home/rizz/dev/*`.
- **Multi-Harness Transcript Extraction**: Extracts compact, token-efficient session summaries (user goal, tools executed, errors encountered, last conversation turn) from Antigravity, Antigravity CLI, Antigravity IDE, and Claude Code.
- **Local Skill Shadowing (`prompt-architect`)**: Embedded locally in `.agents/skills/prompt-architect/` and `.claude/skills/prompt-architect/` so local adjustments remain isolated without modifying global machine skills.
- **Full Studio Suite CLI (`prompt-eng`)**:
  - `prompt-eng scan`: Pindai seluruh repo `/dev/*` dan hasilkan profil `repos/<name>/profile.yaml`.
  - `prompt-eng transcript --repo <name>`: Ekstrak ringkasan sesi aktif.
  - `prompt-eng score "<prompt>"`: Hitung skor rubrik 5-dimensi (Clarity, Specificity, Context, Completeness, Structure).
  - `prompt-eng diff <before> <after>`: Visualisasi perbandingan prompt berwarna di terminal.
  - `prompt-eng list` & `prompt-eng search <query>`: Katalog dan pencarian prompt lintas-repo.
  - `prompt-eng save-prompt`: Simpan prompt terstruktur dengan YAML frontmatter.

## 🚀 Quickstart

```bash
# 1. Pindai seluruh repositori di /home/rizz/dev/
bin/prompt-eng scan

# 2. Lihat profil repo target
bin/prompt-eng profile 0x-arbiter

# 3. Evaluasi skor prompt
bin/prompt-eng score "Fix auth middleware to use bearer token"

# 4. Ekstrak transkrip sesi terakhir
bin/prompt-eng transcript --repo 0x-arbiter

# 5. Jalankan unit test
python3 -m unittest discover -s tests
```

## 📐 Architecture & Standards
Detailed design specifications are available in [`docs/superpowers/specs/2026-09-22-prompt-engineer-hub-design.md`](docs/superpowers/specs/2026-09-22-prompt-engineer-hub-design.md).
