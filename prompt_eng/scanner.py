"""Multi-repository scanner to detect stack, harness instructions, and invariants."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from prompt_eng.models import HarnessInfo, RepoProfile, StackInfo, dump_yaml_simple


def scan_repository(repo_path: Path) -> RepoProfile:
    """Scan a single repository directory to detect its stack, harness, and invariants."""
    name = repo_path.name
    stack = StackInfo()
    harness = HarnessInfo()
    invariants: list[str] = []
    description = ""

    # Detect package & build manifests
    if (repo_path / "pyproject.toml").exists():
        stack.language = "python"
        content = (repo_path / "pyproject.toml").read_text(encoding="utf-8", errors="ignore")
        stack.package_manager = "uv" if "uv" in content else "pip/poetry"
        stack.test_framework = "pytest" if "pytest" in content else "unittest"
        stack.linter = "ruff" if "ruff" in content else "flake8"
        desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
        if desc_match:
            description = desc_match.group(1).strip()
    elif (
        (repo_path / "requirements.txt").exists()
        or (repo_path / "setup.py").exists()
        or (repo_path / "uv.lock").exists()
    ):
        stack.language = "python"
        stack.package_manager = "uv" if (repo_path / "uv.lock").exists() else "pip"
        stack.test_framework = (
            "pytest"
            if (repo_path / "tests").exists() or (repo_path / "pytest.ini").exists()
            else "unittest"
        )
        stack.linter = (
            "ruff"
            if (repo_path / "ruff.toml").exists() or (repo_path / ".ruff.toml").exists()
            else "flake8"
        )
        if (repo_path / "setup.py").exists():
            content = (repo_path / "setup.py").read_text(encoding="utf-8", errors="ignore")
            desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
            if desc_match:
                description = desc_match.group(1).strip()
    elif (repo_path / "package.json").exists():
        stack.language = "javascript/typescript"
        content = (repo_path / "package.json").read_text(encoding="utf-8", errors="ignore")
        stack.package_manager = "pnpm" if (repo_path / "pnpm-lock.yaml").exists() else "npm"
        stack.test_framework = (
            "jest" if "jest" in content else "vitest" if "vitest" in content else "npm test"
        )
        stack.linter = "eslint" if "eslint" in content else "prettier"
        desc_match = re.search(r'"description"\s*:\s*"([^"]+)"', content)
        if desc_match:
            description = desc_match.group(1).strip()
    elif (repo_path / "Cargo.toml").exists():
        stack.language = "rust"
        stack.package_manager = "cargo"
        stack.test_framework = "cargo test"
        stack.linter = "clippy"
    elif (repo_path / "go.mod").exists():
        stack.language = "go"
        stack.package_manager = "go modules"
        stack.test_framework = "go test"
        stack.linter = "golangci-lint"

    # Always ensure uv.lock overrides package_manager to uv
    if (repo_path / "uv.lock").exists():
        stack.package_manager = "uv"

    # Detect harness files
    for doc in ["AGENTS.md", "CLAUDE.md", "GEMINI.md", "CONTEXT.md"]:
        doc_path = repo_path / doc
        if doc_path.exists():
            harness.instruction_files.append(doc)
            text = doc_path.read_text(encoding="utf-8", errors="ignore")
            in_invariant_section = False
            in_pointer_section = False
            for line in text.splitlines():
                stripped = line.strip()
                if stripped.startswith("#"):
                    header_lower = stripped.lower()
                    in_pointer_section = any(
                        k in header_lower
                        for k in ["pointer", "reference", "link", "table of content"]
                    )
                    in_invariant_section = (not in_pointer_section) and any(
                        k in header_lower
                        for k in [
                            "invariant",
                            "guardrail",
                            "rule",
                            "verification gate",
                            "sop",
                            "contract",
                        ]
                    )
                if not in_pointer_section and stripped.startswith(("- ", "* ")):
                    inv_item = stripped[2:].strip()
                    is_match = in_invariant_section or any(
                        k in stripped.lower()
                        for k in [
                            "test",
                            "rule",
                            "invariant",
                            "require",
                            "never",
                            "must",
                            "prohibit",
                            "isolate",
                            "boundary",
                            "freeze",
                            "zero-stall",
                        ]
                    )
                    if is_match and inv_item and inv_item not in invariants:
                        invariants.append(inv_item)

    # Detect additional key instruction docs and specs
    for extra_doc in [
        repo_path / "docs" / "PRD.md",
        repo_path / ".scratch" / "HANDOFF.md",
    ]:
        if extra_doc.exists():
            rel_doc = extra_doc.relative_to(repo_path).as_posix()
            if rel_doc not in harness.instruction_files:
                harness.instruction_files.append(rel_doc)

    specs_dir = repo_path / "docs" / "specs"
    if specs_dir.exists() and specs_dir.is_dir():
        for spec_file in sorted(specs_dir.glob("*/spec.md")):
            rel_spec = spec_file.relative_to(repo_path).as_posix()
            if rel_spec not in harness.instruction_files:
                harness.instruction_files.append(rel_spec)

    # Detect terms and system invariants from CONTEXT.md
    context_doc = repo_path / "CONTEXT.md"
    if context_doc.exists():
        c_text = context_doc.read_text(encoding="utf-8", errors="ignore")
        term_blocks = re.findall(
            r"\*\*([^*]+(?:Invariant|Gate|Protocol|Demarcation|Boundary|Enclosure))\*\*:\s*\n?(.*?)(?=\n_Avoid_|\n\n|\Z)",
            c_text,
            re.DOTALL,
        )
        for term, definition in term_blocks:
            clean_def = " ".join(definition.strip().splitlines())
            item = f"**{term}**: {clean_def}"
            if item not in invariants:
                invariants.append(item)

    # Detect skills
    for skill_dir in [
        repo_path / ".agents" / "skills",
        repo_path / ".claude" / "skills",
        repo_path / "components" / "skills",
    ]:
        if skill_dir.exists() and skill_dir.is_dir():
            for child in sorted(skill_dir.iterdir(), key=lambda p: p.name):
                if (
                    child.is_dir()
                    and (child / "SKILL.md").exists()
                    and child.name not in harness.active_skills
                ):
                    harness.active_skills.append(child.name)

    # Detect rules
    for rules_dir in [
        repo_path / ".agents" / "rules",
        repo_path / ".claude" / "rules",
        repo_path / "rules",
    ]:
        if rules_dir.exists() and rules_dir.is_dir():
            for child in sorted(rules_dir.iterdir(), key=lambda p: p.name):
                if (
                    child.is_file()
                    and child.suffix in [".md", ".markdown"]
                    and child.name not in harness.rules
                ):
                    harness.rules.append(child.name)

    # Detect staged design blueprints
    blueprints: list[str] = []
    staged_dir = repo_path / "components" / "staged"
    if staged_dir.exists() and staged_dir.is_dir():
        for child in sorted(staged_dir.iterdir(), key=lambda p: p.name):
            if child.is_file() and child.name.endswith(".md"):
                blueprints.append(child.name)

    # Detect inspired component corpus
    inspired_corpus: dict[str, int] = {}
    inspired_dir = repo_path / "components" / "inspired"
    if inspired_dir.exists() and inspired_dir.is_dir():
        for cat_dir in sorted(inspired_dir.iterdir(), key=lambda p: p.name):
            if cat_dir.is_dir():
                label_files = list(cat_dir.rglob("*LABEL.md"))
                if label_files:
                    inspired_corpus[cat_dir.name] = len(label_files)
                else:
                    items = [x for x in cat_dir.iterdir() if not x.name.startswith(".")]
                    if items:
                        inspired_corpus[cat_dir.name] = len(items)

    # Detect active milestone
    active_milestone = ""
    roadmaps_dir = repo_path / "docs" / "roadmaps"
    if roadmaps_dir.exists():
        candidates: list[tuple[str, str]] = []
        for r_file in sorted(roadmaps_dir.glob("milestones-*/*.md")):
            if r_file.name == "overview.md":
                continue
            r_text = r_file.read_text(encoding="utf-8", errors="ignore")
            st_match = re.search(r"-\s*\*\*Status:?\*\*:?\s*([^\n]+)", r_text)
            if st_match and "IN PROGRESS" in st_match.group(1).upper():
                h1_match = re.search(r"^#\s+([^\n]+)", r_text, re.MULTILINE)
                name_str = h1_match.group(1).strip() if h1_match else r_file.stem
                raw_status = st_match.group(1).strip().replace("`", "")
                candidates.append((r_file.stem, f"{name_str} [{raw_status}]"))
        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            m12 = next((c[1] for c in candidates if "1.2" in c[0]), None)
            active_milestone = m12 or candidates[0][1]
    if not active_milestone:
        handoff_doc = repo_path / ".scratch" / "HANDOFF.md"
        if handoff_doc.exists():
            h_text = handoff_doc.read_text(encoding="utf-8", errors="ignore")
            m_match = re.search(r"-\s*\*\*Sub-Milestone\*\*:\s*([^\n]+)", h_text)
            s_match = re.search(r"-\s*\*\*Status\*\*:\s*`?([^`\n]+)`?", h_text)
            if m_match:
                sub_m = m_match.group(1).strip()
                status = s_match.group(1).strip() if s_match else ""
                active_milestone = f"{sub_m} [{status}]" if status else sub_m

    # Detect failure gates
    failure_gates: list[str] = []
    for check_file in [
        repo_path / "docs" / "specs" / "005-m1.2-labeling-inspired-components" / "spec.md",
        repo_path / "CONTEXT.md",
        repo_path / "docs" / "audits" / "2026-10-02-skills-audit-report.md",
    ]:
        if check_file.exists():
            content = check_file.read_text(encoding="utf-8", errors="ignore")
            if "Failure Gate" in content:
                failure_gates = [
                    "Workflow Drift (skipping design reviews and verification checkpoints)",
                    "Package Hallucination (invoking unmanifested packages or runtime APIs)",
                    "Context Pollution (dumping raw ASTs or huge files into primary context)",
                    "Hollow Assertion (relying on vacuous mock-only checks without grounded verification)",
                ]
                break

    return RepoProfile(
        name=name,
        path=str(repo_path.resolve()),
        description=description or f"Auto-profiled {stack.language} workspace",
        stack=stack,
        harness=harness,
        invariants=invariants[:25],
        last_scanned=datetime.now(UTC).isoformat(),
        active_milestone=active_milestone,
        blueprints=blueprints,
        inspired_corpus=inspired_corpus,
        failure_gates=failure_gates,
    )


def save_repository_profile(profile: RepoProfile, output_repos_dir: Path) -> Path:
    """Save a RepoProfile to output_repos_dir/<name>/profile.yaml."""
    repo_studio_dir = output_repos_dir / profile.name
    repo_studio_dir.mkdir(parents=True, exist_ok=True)
    (repo_studio_dir / "prompts").mkdir(exist_ok=True)

    meta: dict[str, Any] = {
        "name": profile.name,
        "path": profile.path,
        "description": profile.description,
        "stack": {
            "language": profile.stack.language,
            "package_manager": profile.stack.package_manager,
            "test_framework": profile.stack.test_framework,
            "linter": profile.stack.linter,
        },
        "harness": {
            "instruction_files": profile.harness.instruction_files,
            "active_skills": profile.harness.active_skills,
            "rules": profile.harness.rules,
        },
        "invariants": profile.invariants,
        "last_scanned": profile.last_scanned,
    }
    if profile.active_milestone:
        meta["active_milestone"] = profile.active_milestone
    if profile.blueprints:
        meta["blueprints"] = profile.blueprints
    if profile.inspired_corpus:
        meta["inspired_corpus"] = profile.inspired_corpus
    if profile.failure_gates:
        meta["failure_gates"] = profile.failure_gates

    profile_path = repo_studio_dir / "profile.yaml"
    profile_path.write_text(dump_yaml_simple(meta) + "\n", encoding="utf-8")
    return profile_path


def scan_all_repositories(dev_root: Path, output_repos_dir: Path) -> list[RepoProfile]:
    """Scan all repositories under dev_root and write profiles to output_repos_dir."""
    profiles: list[RepoProfile] = []
    output_repos_dir.mkdir(parents=True, exist_ok=True)

    for item in sorted(dev_root.iterdir(), key=lambda p: p.name):
        if (
            not item.is_dir()
            or item.name.startswith(".")
            or item.name in ["prompt-engineer", "repos"]
        ):
            continue
        # Skip temporary folders
        if "delete this" in item.name.lower():
            continue

        profile = scan_repository(item)
        profiles.append(profile)
        save_repository_profile(profile, output_repos_dir)

    return profiles
