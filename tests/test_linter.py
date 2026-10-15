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

    def test_lint_detects_got_and_meta_prompting_incomplete(self):
        bad_got = "## Objective\nSolve problem."
        report = lint_prompt(bad_got, framework="GOT")
        self.assertFalse(report.is_valid)
        self.assertTrue(
            any(
                i.rule_id == "ERR-FRAMEWORK-INCOMPLETE" and "Graph Topology" in i.message
                for i in report.issues
            )
        )

        bad_meta = "## Objective\nSolve problem."
        report_meta = lint_prompt(bad_meta, framework="META-PROMPTING")
        self.assertFalse(report_meta.is_valid)
        self.assertTrue(
            any(
                i.rule_id == "ERR-FRAMEWORK-INCOMPLETE"
                and "Conductor System Instructions" in i.message
                for i in report_meta.issues
            )
        )

    def test_lint_detects_react_incomplete(self):
        bad_react = "## System Instructions\nDo something."
        report = lint_prompt(bad_react, framework="REACT")
        self.assertFalse(report.is_valid)
        self.assertTrue(
            any(
                i.rule_id == "ERR-FRAMEWORK-INCOMPLETE" and "Goal" in i.message
                for i in report.issues
            )
        )

    def test_lint_scaffolded_react_clean(self):
        from prompt_eng.studio.scaffolder import scaffold_prompt

        _, body_react = scaffold_prompt(self.profile, "test-repo", "react-task", framework="REACT")
        report = lint_prompt(body_react, self.profile, framework="REACT")
        self.assertFalse(report.has_errors)

    def test_lint_detects_naive_negation_warning(self):
        neg_prompt = """## Role
You are an assistant.
## Steps
Do not use var. Never use any. Don’t mutate state. Cannot import lodash.
## Output
Return code.
"""
        report = lint_prompt(neg_prompt, strict=False)
        self.assertTrue(report.is_valid)  # Warning only by default
        self.assertTrue(any(i.rule_id == "WARN-NAIVE-NEGATION" for i in report.issues))

        strict_report = lint_prompt(neg_prompt, strict=True)
        self.assertFalse(strict_report.is_valid)  # Strict mode fails on warnings

    def test_lint_balanced_negative_constraints_no_warning(self):
        balanced_prompt = """## Role
You are an expert engineer.
## Steps
Do not use var. Never mutate state. Don't use any.
You must use const, only use pure functions, and ensure type safety.
## Output
Return verified code.
"""
        report = lint_prompt(balanced_prompt, strict=True)
        self.assertFalse(any(i.rule_id == "WARN-NAIVE-NEGATION" for i in report.issues))

    def test_lint_detects_sandwich_structure_warning(self):
        # A long prompt (>150 words) that lacks head or tail anchors
        middle_heavy = (
            "Here is a task. " + "We have many instructions in the middle. " * 30 + "Just do it."
        )
        report = lint_prompt(middle_heavy)
        self.assertTrue(any(i.rule_id == "WARN-SANDWICH-STRUCTURE" for i in report.issues))

    def test_lint_scaffolded_got_and_meta_prompting_clean(self):
        from prompt_eng.studio.scaffolder import scaffold_prompt

        _, body_got = scaffold_prompt(None, "test-repo", "got-task", framework="GOT")
        report_got = lint_prompt(body_got, framework="GOT", strict=True)
        self.assertTrue(report_got.is_valid)
        self.assertFalse(any(i.rule_id == "WARN-SANDWICH-STRUCTURE" for i in report_got.issues))

        _, body_meta = scaffold_prompt(None, "test-repo", "meta-task", framework="META-PROMPTING")
        report_meta = lint_prompt(body_meta, framework="META-PROMPTING", strict=True)
        self.assertTrue(report_meta.is_valid)
        self.assertFalse(any(i.rule_id == "WARN-SANDWICH-STRUCTURE" for i in report_meta.issues))

    def test_lint_detects_client_secret_leak_warning(self):
        leak_prompt = """## Component
'use client'
import React from 'react';
const secret = process.env.STRIPE_SECRET_KEY;
"""
        report = lint_prompt(leak_prompt)
        self.assertTrue(any(i.rule_id == "WARN-CLIENT-SECRET-LEAK" for i in report.issues))

    def test_lint_client_public_env_no_leak_warning(self):
        public_prompt = """## Component
'use client'
import React from 'react';
const apiKey = process.env.NEXT_PUBLIC_STRIPE_KEY;
const viteKey = process.env.VITE_APP_KEY;
"""
        report = lint_prompt(public_prompt)
        self.assertFalse(any(i.rule_id == "WARN-CLIENT-SECRET-LEAK" for i in report.issues))

    def test_lint_detects_bot_and_medprompt_incomplete(self):
        bad_bot = "## Objective\nSolve problem."
        report_bot = lint_prompt(bad_bot, framework="BOT")
        self.assertFalse(report_bot.is_valid)
        self.assertTrue(
            any(
                i.rule_id == "ERR-FRAMEWORK-INCOMPLETE" and "Distilled Meta-Buffer" in i.message
                for i in report_bot.issues
            )
        )

        bad_med = "## Objective\nSolve problem."
        report_med = lint_prompt(bad_med, framework="MEDPROMPT")
        self.assertFalse(report_med.is_valid)
        self.assertTrue(
            any(
                i.rule_id == "ERR-FRAMEWORK-INCOMPLETE" and "Choice-Shuffle Ensembling" in i.message
                for i in report_med.issues
            )
        )


if __name__ == "__main__":
    unittest.main()
