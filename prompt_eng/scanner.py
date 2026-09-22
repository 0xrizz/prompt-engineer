"""Multi-repository scanner to detect stack, harness instructions, and invariants."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

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
    for doc in ["AGENTS.md", "CLAUDE.md", "GEMINI.md"]:
        doc_path = repo_path / doc
        if doc_path.exists():
            harness.instruction_files.append(doc)
            text = doc_path.read_text(encoding="utf-8", errors="ignore")
            for line in text.splitlines():
                stripped = line.strip()
                if stripped.startswith("- ") and any(
                    k in stripped.lower() for k in ["test", "rule", "invariant", "require", "never"]
                ):
                    inv_item = stripped[2:].strip()
                    if inv_item and inv_item not in invariants:
                        invariants.append(inv_item)

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

    return RepoProfile(
        name=name,
        path=str(repo_path.resolve()),
        description=description or f"Auto-profiled {stack.language} workspace",
        stack=stack,
        harness=harness,
        invariants=invariants[:10],
        last_scanned=datetime.now(UTC).isoformat(),
    )


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

        # Write to repos/<name>/profile.yaml
        repo_studio_dir = output_repos_dir / profile.name
        repo_studio_dir.mkdir(parents=True, exist_ok=True)
        (repo_studio_dir / "prompts").mkdir(exist_ok=True)

        meta = {
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
            },
            "invariants": profile.invariants,
            "last_scanned": profile.last_scanned,
        }
        (repo_studio_dir / "profile.yaml").write_text(
            dump_yaml_simple(meta) + "\n", encoding="utf-8"
        )

    return profiles
