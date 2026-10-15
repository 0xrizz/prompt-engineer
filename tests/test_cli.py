import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CLIResult(subprocess.CompletedProcess):
    """CompletedProcess subclass enabling string membership assertions on output and scaffolded files."""

    def __contains__(self, item: object) -> bool:
        if not isinstance(item, str):
            return False
        if item in self.stdout or item in self.stderr:
            return True
        for line in self.stdout.splitlines():
            if "Scaffolded" in line and "at " in line:
                path_str = line.split("at ", 1)[1].strip()
                p = Path(path_str)
                if p.exists() and item in p.read_text(encoding="utf-8"):
                    return True
        return False


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent
        self.bin = self.root / "bin" / "prompt-eng"

    def tearDown(self):
        test_repo_dir = self.root / "repos" / "test-repo"
        if test_repo_dir.exists():
            import shutil

            shutil.rmtree(test_repo_dir)

    def run_cli(self, args, env=None):
        cli_env = os.environ.copy()
        if env:
            cli_env.update(env)
        res = subprocess.run(
            [sys.executable, str(self.bin)] + args,
            capture_output=True,
            text=True,
            env=cli_env,
            check=False,
        )
        return CLIResult(res.args, res.returncode, res.stdout, res.stderr)

    def test_help_command(self):
        res = self.run_cli(["--help"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("scan", res.stdout)
        self.assertIn("transcript", res.stdout)
        self.assertIn("score", res.stdout)
        self.assertIn("diff", res.stdout)
        self.assertIn("list", res.stdout)
        self.assertIn("search", res.stdout)
        self.assertIn("save-prompt", res.stdout)

    def test_no_args_prints_help(self):
        res = self.run_cli([])
        self.assertEqual(res.returncode, 0)
        self.assertIn("Centralized Prompt Engineering Studio", res.stdout)

    def test_score_command_text(self):
        res = self.run_cli(["score", "Write a python unit test for auth middleware"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("Clarity", res.stdout)
        self.assertIn("Overall", res.stdout)

    def test_score_command_file(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("Role: Senior Dev\nTask: Build unit test\nFormat: Python unittest")
            f_path = f.name
        try:
            res = self.run_cli(["score", "--file", f_path])
            self.assertEqual(res.returncode, 0)
            self.assertIn("Clarity", res.stdout)
            self.assertIn("Overall", res.stdout)
        finally:
            if Path(f_path).exists():
                Path(f_path).unlink()

    def test_score_command_missing_input(self):
        res = self.run_cli(["score"])
        self.assertEqual(res.returncode, 1)
        self.assertIn("Error: Must provide prompt text or --file", res.stderr)

    def test_list_command(self):
        res = self.run_cli(["list"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("Tracked Repositories", res.stdout)

    def test_diff_command(self):
        res = self.run_cli(["diff", "Hello world", "Hello brave new world"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("Original Prompt", res.stdout)
        self.assertIn("Optimized Prompt", res.stdout)

    def test_save_prompt_and_search_command(self):
        test_repo_dir = self.root / "repos" / "test-repo"
        try:
            # Run save-prompt with content
            res_save = self.run_cli(
                [
                    "save-prompt",
                    "--repo",
                    "test-repo",
                    "--name",
                    "auth-test",
                    "--framework",
                    "RISEN",
                    "--content",
                    "Role: Tester\nTask: Validate authentication token handling\nSteps: Test invalid tokens",
                ]
            )
            self.assertEqual(res_save.returncode, 0)
            self.assertIn("Saved engineered prompt", res_save.stdout)

            # Verify search finds it
            res_search = self.run_cli(["search", "authentication"])
            self.assertEqual(res_search.returncode, 0)
            self.assertIn("test-repo", res_search.stdout)
            self.assertIn("auth-test.md", res_search.stdout)
        finally:
            # Cleanup created files in repos/test-repo
            if test_repo_dir.exists():
                import shutil

                shutil.rmtree(test_repo_dir)

    def test_transcript_command_with_file(self):
        fixture = self.root / "tests" / "fixtures" / "antigravity_sample.jsonl"
        res = self.run_cli(["transcript", "--repo", "sample-repo", "--file", str(fixture)])
        self.assertEqual(res.returncode, 0)
        self.assertIn("Session Context Summary", res.stdout)
        self.assertIn("sample-repo", res.stdout)

    def test_transcript_command_json_format(self):
        fixture = self.root / "tests" / "fixtures" / "antigravity_sample.jsonl"
        res = self.run_cli(
            ["transcript", "--repo", "sample-repo", "--file", str(fixture), "--format", "json"]
        )
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertEqual(data["repo_name"], "sample-repo")
        self.assertEqual(data["harness"], "antigravity")
        self.assertIn("Fix the failing test", data["user_goal"])

    def test_scan_single_repo_cli(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            sample_repo = Path(tmp_dir) / "cli-sample"
            sample_repo.mkdir()
            (sample_repo / "pyproject.toml").write_text(
                '[project]\nname = "cli-sample"\n', encoding="utf-8"
            )
            out_repos = Path(tmp_dir) / "repos"

            # Test scanning by path
            res = self.run_cli(["scan", str(sample_repo), "--output", str(out_repos)])
            self.assertEqual(res.returncode, 0)
            self.assertIn("cli-sample", res.stdout)
            self.assertTrue((out_repos / "cli-sample" / "profile.yaml").exists())

            # Test scanning by --repo flag
            res_flag = self.run_cli(
                ["scan", "--repo", str(sample_repo), "--output", str(out_repos)]
            )
            self.assertEqual(res_flag.returncode, 0)
            self.assertIn("cli-sample", res_flag.stdout)

    def test_scan_single_repo_not_found(self):
        res = self.run_cli(["scan", "/nonexistent/repo/path/xyz"])
        self.assertEqual(res.returncode, 1)
        self.assertIn("Target repository directory not found", res.stderr)

    def test_cli_scaffold_stdout(self):
        res = self.run_cli(
            [
                "scaffold",
                "--repo",
                "sample-repo",
                "--name",
                "test-p",
                "--framework",
                "RISEN",
                "--stdout",
            ]
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("## Role", res.stdout)
        self.assertIn("## Steps", res.stdout)

    def test_cli_lint_clean_and_strict(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(
                "## Role\nEng\n## Input\nIn\n## Steps\n1. Go\n## Expectation\nPass\n## Narrowing\nNone\n"
            )
            f_path = f.name
        try:
            res = self.run_cli(["lint", f_path, "--repo", "cli-sample"])
            self.assertEqual(res.returncode, 0)
            self.assertIn("✓ Lint passed", res.stdout)
        finally:
            Path(f_path).unlink()

    def test_cli_search_json(self):
        res = self.run_cli(["search", "", "--json"])
        self.assertEqual(res.returncode, 0)
        self.assertTrue(res.stdout.strip().startswith("[") or res.stdout.strip().startswith("{"))

    def test_cli_scaffold_got_framework(self):
        output = self.run_cli(
            ["scaffold", "--framework", "got", "--repo", "test-repo", "--name", "dag-task"]
        )
        self.assertIn("framework: GOT", output)
        self.assertIn("## Graph Topology (DAG)", output)

    def test_cli_scaffold_web_accessible(self):
        output = self.run_cli(
            [
                "scaffold",
                "--framework",
                "web-accessible",
                "--repo",
                "test-repo",
                "--name",
                "nav-bar",
            ]
        )
        self.assertIn("framework: WEB-ACCESSIBLE", output)
        self.assertIn("## Semantic Landmark Hierarchy", output)

    def test_cli_scaffold_meta_prompting(self):
        output = self.run_cli(
            ["scaffold", "-f", "meta-prompting", "--repo", "test-repo", "--name", "meta-task"]
        )
        self.assertIn("framework: META-PROMPTING", output)
        self.assertIn("## Conductor System Instructions", output)

    def test_cli_scaffold_bot(self):
        output = self.run_cli(
            ["scaffold", "-f", "bot", "--repo", "test-repo", "--name", "bot-task"]
        )
        self.assertIn("framework: BOT", output)
        self.assertIn("## Distilled Meta-Buffer Templates", output)

    def test_cli_scaffold_medprompt(self):
        output = self.run_cli(
            ["scaffold", "-f", "medprompt", "--repo", "test-repo", "--name", "med-task"]
        )
        self.assertIn("framework: MEDPROMPT", output)
        self.assertIn("## Dynamic Few-Shot Exemplars", output)

    def test_cli_scaffold_defensive_action(self):
        output = self.run_cli(
            ["scaffold", "-f", "defensive-action", "--repo", "test-repo", "--name", "sec-task"]
        )
        self.assertIn("framework: DEFENSIVE-ACTION", output)
        self.assertIn("## Boundary Contract (Server Action)", output)

    def test_cli_scaffold_aliases_and_case(self):
        output1 = self.run_cli(
            [
                "scaffold",
                "--framework",
                "graph-of-thoughts",
                "--repo",
                "test-repo",
                "--name",
                "dag-alias",
            ]
        )
        self.assertIn("## Graph Topology (DAG)", output1)

        output2 = self.run_cli(
            [
                "scaffold",
                "--framework",
                "buffer-of-thoughts",
                "--repo",
                "test-repo",
                "--name",
                "bot-alias",
            ]
        )
        self.assertIn("## Distilled Meta-Buffer Templates", output2)

        output3 = self.run_cli(
            ["scaffold", "-f", "GOT", "--repo", "test-repo", "--name", "dag-upper"]
        )
        self.assertIn("## Graph Topology (DAG)", output3)

        output4 = self.run_cli(
            [
                "scaffold",
                "-f",
                "WEB-ACCESSIBLE",
                "--repo",
                "test-repo",
                "--name",
                "nav-upper",
            ]
        )
        self.assertIn("## Semantic Landmark Hierarchy", output4)

    def test_cli_scaffold_invalid_framework_rejected(self):
        res = self.run_cli(
            ["scaffold", "--framework", "invalid-fw", "--repo", "test-repo", "--name", "bad-task"]
        )
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("invalid choice", res.stderr)

    def test_cli_lint_with_framework_options(self):
        from prompt_eng.studio.scaffolder import scaffold_prompt

        _, got_body = scaffold_prompt(None, "cli-sample", "dag-task", framework="GOT")
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(got_body)
            f_path = f.name
        try:
            # Valid framework passed to lint
            res_valid = self.run_cli(["lint", f_path, "--repo", "cli-sample", "-f", "got"])
            self.assertEqual(res_valid.returncode, 0)
            self.assertIn("✓ Lint passed", res_valid.stdout)

            # Invalid framework passed to lint rejected by argparse
            res_invalid = self.run_cli(["lint", f_path, "--repo", "cli-sample", "-f", "invalid-fw"])
            self.assertNotEqual(res_invalid.returncode, 0)
            self.assertIn("invalid choice", res_invalid.stderr)
        finally:
            Path(f_path).unlink()

    def test_cli_scaffold_framework_alias_canonical_normalization(self):
        # Test graph-of-thoughts maps to got and generates GOT DAG structure
        res_got = self.run_cli(
            [
                "scaffold",
                "--framework",
                "graph-of-thoughts",
                "--repo",
                "test-repo",
                "--name",
                "dag-arch",
                "--stdout",
            ]
        )
        self.assertEqual(res_got.returncode, 0)
        self.assertIn("framework: GOT", res_got.stdout)
        self.assertIn("## Graph Topology (DAG)", res_got.stdout)

        # Test buffer-of-thoughts maps to bot and generates BOT structure
        res_bot = self.run_cli(
            [
                "scaffold",
                "--framework",
                "buffer-of-thoughts",
                "--repo",
                "test-repo",
                "--name",
                "bot-arch",
                "--stdout",
            ]
        )
        self.assertEqual(res_bot.returncode, 0)
        self.assertIn("framework: BOT", res_bot.stdout)
        self.assertIn("## Distilled Meta-Buffer Templates", res_bot.stdout)

    def test_cli_lint_strict_mode(self):
        # A prompt with a warning (e.g. naive negation)
        warn_prompt = (
            "## Role\nEngineer\n"
            "## Input\nTask\n"
            "## Steps\nDo not use var. Never use any. Don't mutate.\n"
            "## Expectation\nDone\n"
            "## Narrowing\nInvariants\n"
        )
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(warn_prompt)
            f_path = f.name
        try:
            # Without strict, exits 0
            res_normal = self.run_cli(["lint", f_path, "--repo", "test-repo", "-f", "risen"])
            self.assertEqual(res_normal.returncode, 0)

            # With strict, exits 1
            res_strict = self.run_cli(
                ["lint", f_path, "--repo", "test-repo", "-f", "risen", "--strict"]
            )
            self.assertEqual(res_strict.returncode, 1)
        finally:
            Path(f_path).unlink()


if __name__ == "__main__":
    unittest.main()
