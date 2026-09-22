from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from prompt_eng.models import load_yaml_simple
from prompt_eng.scanner import scan_all_repositories, scan_repository


class TestScanner(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp_dir.name)

        # Mock repo 1: Python project
        self.repo1 = self.root / "py-service"
        self.repo1.mkdir()
        (self.repo1 / "pyproject.toml").write_text(
            '[project]\nname="py-service"\n# uses uv, pytest, and ruff\n', encoding="utf-8"
        )
        (self.repo1 / "AGENTS.md").write_text(
            "# Py Service Invariants\n- Fast tests always\n- Follow security rule strictly\n",
            encoding="utf-8",
        )

        # Mock repo 2: Node project
        self.repo2 = self.root / "web-app"
        self.repo2.mkdir()
        (self.repo2 / "package.json").write_text(
            '{"name": "web-app", "scripts": {"test": "jest"}, "devDependencies": {"eslint": "^8"}}\n',
            encoding="utf-8",
        )
        (self.repo2 / "CLAUDE.md").write_text(
            "# Claude Guidelines\n- Never push directly to main\n", encoding="utf-8"
        )

        self.output_dir = self.root / "repos"

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_scan_single_repo(self) -> None:
        profile = scan_repository(self.repo1)
        self.assertEqual(profile.name, "py-service")
        self.assertEqual(profile.stack.language, "python")
        self.assertEqual(profile.stack.package_manager, "uv")
        self.assertEqual(profile.stack.test_framework, "pytest")
        self.assertEqual(profile.stack.linter, "ruff")
        self.assertIn("AGENTS.md", profile.harness.instruction_files)
        self.assertIn("Fast tests always", profile.invariants)
        self.assertIn("Follow security rule strictly", profile.invariants)

    def test_scan_node_repo(self) -> None:
        profile = scan_repository(self.repo2)
        self.assertEqual(profile.name, "web-app")
        self.assertEqual(profile.stack.language, "javascript/typescript")
        self.assertEqual(profile.stack.package_manager, "npm")
        self.assertEqual(profile.stack.test_framework, "jest")
        self.assertEqual(profile.stack.linter, "eslint")
        self.assertIn("CLAUDE.md", profile.harness.instruction_files)
        self.assertIn("Never push directly to main", profile.invariants)

    def test_scan_rust_and_go_repositories(self) -> None:
        rust_repo = self.root / "rust-engine"
        rust_repo.mkdir()
        (rust_repo / "Cargo.toml").write_text('[package]\nname = "rust-engine"\n', encoding="utf-8")

        go_repo = self.root / "go-service"
        go_repo.mkdir()
        (go_repo / "go.mod").write_text("module example.com/goservice\n", encoding="utf-8")

        rust_profile = scan_repository(rust_repo)
        self.assertEqual(rust_profile.stack.language, "rust")
        self.assertEqual(rust_profile.stack.package_manager, "cargo")
        self.assertEqual(rust_profile.stack.test_framework, "cargo test")
        self.assertEqual(rust_profile.stack.linter, "clippy")

        go_profile = scan_repository(go_repo)
        self.assertEqual(go_profile.stack.language, "go")
        self.assertEqual(go_profile.stack.package_manager, "go modules")
        self.assertEqual(go_profile.stack.test_framework, "go test")
        self.assertEqual(go_profile.stack.linter, "golangci-lint")

    def test_scan_skills_detection(self) -> None:
        skills_repo = self.root / "skilled-app"
        skills_repo.mkdir()
        (skills_repo / "pyproject.toml").write_text(
            '[project]\nname="skilled-app"\n', encoding="utf-8"
        )

        # Create skills across multiple directories
        skill1_dir = skills_repo / ".agents" / "skills" / "my-skill"
        skill1_dir.mkdir(parents=True)
        (skill1_dir / "SKILL.md").write_text("# My Skill\n", encoding="utf-8")

        skill2_dir = skills_repo / ".claude" / "skills" / "claude-skill"
        skill2_dir.mkdir(parents=True)
        (skill2_dir / "SKILL.md").write_text("# Claude Skill\n", encoding="utf-8")

        # Duplicate skill name should be deduplicated
        skill3_dir = skills_repo / "components" / "skills" / "my-skill"
        skill3_dir.mkdir(parents=True)
        (skill3_dir / "SKILL.md").write_text("# My Skill Duplicate\n", encoding="utf-8")

        profile = scan_repository(skills_repo)
        self.assertIn("my-skill", profile.harness.active_skills)
        self.assertIn("claude-skill", profile.harness.active_skills)
        self.assertEqual(profile.harness.active_skills.count("my-skill"), 1)

    def test_scan_all_repositories(self) -> None:
        # Also create folders/files that should be ignored
        (self.root / ".hidden-dir").mkdir()
        (self.root / "prompt-engineer").mkdir()
        (self.root / "some-temp delete this folder").mkdir()
        (self.root / "README.txt").write_text("not a dir", encoding="utf-8")

        profiles = scan_all_repositories(self.root, self.output_dir)
        # Should only find repo1 and repo2
        self.assertEqual(len(profiles), 2)
        repo_names = {p.name for p in profiles}
        self.assertEqual(repo_names, {"py-service", "web-app"})

        p1_file = self.output_dir / "py-service" / "profile.yaml"
        p2_file = self.output_dir / "web-app" / "profile.yaml"
        self.assertTrue(p1_file.exists())
        self.assertTrue(p2_file.exists())

        p1_prompts = self.output_dir / "py-service" / "prompts"
        self.assertTrue(p1_prompts.is_dir())

        # Verify profile content parses back properly
        loaded = load_yaml_simple(p1_file.read_text(encoding="utf-8"))
        self.assertEqual(loaded["name"], "py-service")
        self.assertEqual(loaded["stack"]["language"], "python")
        self.assertIn("Fast tests always", loaded["invariants"])

    def test_deduplicate_invariants(self) -> None:
        dedup_repo = self.root / "dedup-repo"
        dedup_repo.mkdir()
        (dedup_repo / "AGENTS.md").write_text(
            "- Always run tests before commit\n- Follow rule A\n- Always run tests before commit\n",
            encoding="utf-8",
        )
        (dedup_repo / "CLAUDE.md").write_text(
            "- Follow rule A\n- Another requirement\n",
            encoding="utf-8",
        )
        profile = scan_repository(dedup_repo)
        self.assertEqual(profile.invariants.count("Always run tests before commit"), 1)
        self.assertEqual(profile.invariants.count("Follow rule A"), 1)
        self.assertIn("Another requirement", profile.invariants)

    def test_scan_uv_lock_detection(self) -> None:
        uv_repo = self.root / "uv-repo"
        uv_repo.mkdir()
        (uv_repo / "uv.lock").write_text("# uv lockfile\n", encoding="utf-8")
        profile = scan_repository(uv_repo)
        self.assertEqual(profile.stack.language, "python")
        self.assertEqual(profile.stack.package_manager, "uv")

    def test_scan_requirements_and_setup_py(self) -> None:
        pip_repo = self.root / "pip-repo"
        pip_repo.mkdir()
        (pip_repo / "requirements.txt").write_text("pytest>=7.0\n", encoding="utf-8")
        profile = scan_repository(pip_repo)
        self.assertEqual(profile.stack.language, "python")
        self.assertEqual(profile.stack.package_manager, "pip")

        setup_repo = self.root / "setup-repo"
        setup_repo.mkdir()
        (setup_repo / "setup.py").write_text(
            'from setuptools import setup\nsetup(name="pkg", description="Setup package")\n',
            encoding="utf-8",
        )
        profile_setup = scan_repository(setup_repo)
        self.assertEqual(profile_setup.stack.language, "python")
        self.assertEqual(profile_setup.description, "Setup package")

    def test_description_extraction(self) -> None:
        py_repo = self.root / "desc-py"
        py_repo.mkdir()
        (py_repo / "pyproject.toml").write_text(
            '[project]\nname = "desc-py"\ndescription = "High-performance data engine"\n',
            encoding="utf-8",
        )
        profile_py = scan_repository(py_repo)
        self.assertEqual(profile_py.description, "High-performance data engine")

        node_repo = self.root / "desc-node"
        node_repo.mkdir()
        (node_repo / "package.json").write_text(
            '{"name": "desc-node", "description": "Interactive Web Client"}\n',
            encoding="utf-8",
        )
        profile_node = scan_repository(node_repo)
        self.assertEqual(profile_node.description, "Interactive Web Client")


if __name__ == "__main__":
    unittest.main()
