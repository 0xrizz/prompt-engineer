import unittest

from prompt_eng.models import RepoProfile, StackInfo
from prompt_eng.studio.linter import lint_prompt


class TestLinter(unittest.TestCase):
    def setUp(self):
        self.profile = RepoProfile(
            name="py-service",
            path="/home/rizz/dev/py-service",
            description="Python service",
            stack=StackInfo(
                language="Python",
                package_manager="uv",
                test_framework="pytest",
                linter="ruff",
            ),
            invariants=[
                "Fast offline unit tests: uv run pytest tests/",
                "No unmanifested packages",
            ],
            failure_gates=["Workflow Drift"],
        )

    def test_lint_detects_toolchain_mismatch_error(self):
        bad_prompt = "Run npm install and execute npm test to check everything."
        report = lint_prompt(bad_prompt, self.profile, framework="RISEN")
        self.assertFalse(report.is_valid)
        self.assertTrue(report.has_errors)
        error_rules = [i.rule_id for i in report.issues if i.severity == "ERROR"]
        self.assertIn("ERR-TOOLCHAIN-MISMATCH", error_rules)

    def test_lint_detects_missing_framework_sections(self):
        incomplete_risen = "## Role\nEngineer\n## Input\nData\nSome stuff here."
        report = lint_prompt(incomplete_risen, self.profile, framework="RISEN")
        self.assertTrue(report.has_errors)
        error_rules = [i.rule_id for i in report.issues if i.severity == "ERROR"]
        self.assertIn("ERR-FRAMEWORK-INCOMPLETE", error_rules)

    def test_lint_detects_vague_words_warning(self):
        valid_risen = (
            "## Role\nStaff Engineer\n"
            "## Input\nSpecs\n"
            "## Steps\n1. Run tests\n"
            "## Expectation\nPass\n"
            "## Narrowing\nInvariants\n"
            "Maybe we should do something about that thing."
        )
        report = lint_prompt(valid_risen, self.profile, framework="RISEN")
        self.assertFalse(report.has_errors)
        self.assertTrue(report.has_warnings)
        warning_rules = [i.rule_id for i in report.issues if i.severity == "WARNING"]
        self.assertIn("WARN-VAGUE-LANGUAGE", warning_rules)

    def test_lint_detects_js_toolchain_mismatch(self):
        js_profile = RepoProfile(
            name="web-ui",
            path="/home/rizz/dev/web-ui",
            stack=StackInfo(
                language="TypeScript",
                package_manager="npm",
                test_framework="vitest",
                linter="eslint",
            ),
        )
        prompt = "Run uv run pytest to verify the frontend components."
        report = lint_prompt(prompt, js_profile)
        self.assertFalse(report.is_valid)
        self.assertTrue(report.has_errors)
        error_rules = [i.rule_id for i in report.issues if i.severity == "ERROR"]
        self.assertIn("ERR-TOOLCHAIN-MISMATCH", error_rules)

    def test_lint_detects_costar_and_bab_incomplete(self):
        costar_incomplete = "## Context\nTest\n## Objective\nRefactor\n"
        report_costar = lint_prompt(costar_incomplete, None, framework="CO-STAR")
        self.assertTrue(report_costar.has_errors)
        error_rules_costar = [i.rule_id for i in report_costar.issues if i.severity == "ERROR"]
        self.assertIn("ERR-FRAMEWORK-INCOMPLETE", error_rules_costar)

        bab_incomplete = "## Before\nLegacy code\n"
        report_bab = lint_prompt(bab_incomplete, None, framework="BAB")
        self.assertTrue(report_bab.has_errors)
        error_rules_bab = [i.rule_id for i in report_bab.issues if i.severity == "ERROR"]
        self.assertIn("ERR-FRAMEWORK-INCOMPLETE", error_rules_bab)

    def test_lint_strict_mode_fails_on_warning(self):
        prompt_with_warning = (
            "## Role\nStaff Engineer\n"
            "## Input\nSpecs\n"
            "## Steps\n1. Run tests\n"
            "## Expectation\nPass\n"
            "## Narrowing\nInvariants\n"
            "Maybe we should do something about that thing."
        )
        report_normal = lint_prompt(
            prompt_with_warning, self.profile, framework="RISEN", strict=False
        )
        self.assertTrue(report_normal.is_valid)

        report_strict = lint_prompt(
            prompt_with_warning, self.profile, framework="RISEN", strict=True
        )
        self.assertFalse(report_strict.is_valid)

    def test_lint_valid_clean_prompt(self):
        clean_risen = (
            "## Role\nExpert Systems Architect\n"
            "## Input\nTask specifications and repository requirements\n"
            "## Steps\n1. Run unit test suite using uv run pytest\n"
            "## Expectation\nAll 15 assertions must return json format with valid output\n"
            "## Narrowing\nIn order to preserve backward compatibility in repo using version 2.0"
        )
        report = lint_prompt(clean_risen, self.profile, framework="RISEN")
        self.assertTrue(report.is_valid)
        self.assertFalse(report.has_errors)
        self.assertFalse(report.has_warnings)


if __name__ == "__main__":
    unittest.main()
