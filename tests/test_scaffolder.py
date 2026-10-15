import unittest

from prompt_eng.models import HarnessInfo, RepoProfile, StackInfo
from prompt_eng.studio.scaffolder import scaffold_prompt


class TestScaffolder(unittest.TestCase):
    def setUp(self):
        self.profile = RepoProfile(
            name="py-service",
            path="/home/rizz/dev/py-service",
            description="High throughput indexing service",
            stack=StackInfo(
                language="Python",
                package_manager="uv",
                test_framework="pytest",
                linter="ruff",
            ),
            harness=HarnessInfo(
                instruction_files=["AGENTS.md"],
                active_skills=["prompt-architect"],
                rules=["safety.md"],
            ),
            invariants=[
                "Fast offline unit tests: uv run pytest tests/",
                "No unmanifested runtime packages",
            ],
            failure_gates=["Workflow Drift Gate"],
        )

    def test_scaffold_risen_framework(self):
        meta, body = scaffold_prompt(
            self.profile,
            repo_name="py-service",
            prompt_name="add-auth",
            framework="RISEN",
        )
        self.assertEqual(meta["name"], "add-auth")
        self.assertEqual(meta["repo"], "py-service")
        self.assertEqual(meta["framework"], "RISEN")
        self.assertIn("## Role", body)
        self.assertIn("## Input", body)
        self.assertIn("## Steps", body)
        self.assertIn("## Expectation", body)
        self.assertIn("## Narrowing", body)
        self.assertIn("Fast offline unit tests", body)
        self.assertIn("Workflow Drift Gate", body)

    def test_scaffold_costar_framework(self):
        meta, body = scaffold_prompt(
            self.profile,
            repo_name="py-service",
            prompt_name="promo-copy",
            framework="CO-STAR",
        )
        self.assertEqual(meta["framework"], "CO-STAR")
        self.assertIn("## Context", body)
        self.assertIn("## Objective", body)
        self.assertIn("## Style", body)
        self.assertIn("## Tone", body)
        self.assertIn("## Audience", body)
        self.assertIn("## Response", body)

    def test_scaffold_without_profile(self):
        meta, body = scaffold_prompt(
            None,
            repo_name="unknown-repo",
            prompt_name="quick-fix",
            framework="BAB",
        )
        self.assertEqual(meta["framework"], "BAB")
        self.assertIn("## Before", body)
        self.assertIn("## After", body)
        self.assertIn("## Bridge", body)

    def test_scaffold_react_framework(self):
        meta, body = scaffold_prompt(
            self.profile,
            repo_name="py-service",
            prompt_name="debug-issue",
            framework="ReAct",
        )
        self.assertEqual(meta["framework"], "REACT")
        self.assertIn("## System Instructions", body)
        self.assertIn("## Invariants & Guardrails", body)
        self.assertIn("## Goal", body)
        self.assertIn("uv run pytest", body)

    def test_scaffold_fallback_framework(self):
        meta, body = scaffold_prompt(
            self.profile,
            repo_name="py-service",
            prompt_name="custom-task",
            framework="CUSTOM",
        )
        self.assertEqual(meta["framework"], "CUSTOM")
        self.assertIn("## Role & Context", body)
        self.assertIn("## Instructions", body)
        self.assertIn("## Guardrails & Invariants", body)

    def test_scaffold_got_framework(self):
        meta, body = scaffold_prompt(self.profile, "test-repo", "dag-planner", "GOT")
        self.assertEqual(meta["framework"], "GOT")
        self.assertIn("## Graph Topology (DAG)", body)
        self.assertIn("## Generation Nodes", body)
        self.assertIn("## Aggregation & Scoring", body)
        self.assertIn("## Refinement & Exit Criteria", body)

    def test_scaffold_meta_prompting_framework(self):
        meta, body = scaffold_prompt(
            self.profile, "test-repo", "conductor-orchestration", "META-PROMPTING"
        )
        self.assertEqual(meta["framework"], "META-PROMPTING")
        self.assertIn("## Conductor System Instructions", body)
        self.assertIn("## Specialist Agent Personas", body)
        self.assertIn("## Isolated Delegation Protocol", body)

    def test_scaffold_bot_framework(self):
        meta, body = scaffold_prompt(self.profile, "test-repo", "thought-buffer", "BOT")
        self.assertEqual(meta["framework"], "BOT")
        self.assertIn("## Distilled Meta-Buffer Templates", body)
        self.assertIn("## Problem Distillation", body)

    def test_scaffold_medprompt_framework(self):
        meta, body = scaffold_prompt(self.profile, "test-repo", "clinical-eval", "MEDPROMPT")
        self.assertEqual(meta["framework"], "MEDPROMPT")
        self.assertIn("## Dynamic Few-Shot Exemplars", body)
        self.assertIn("## Choice-Shuffle Ensembling", body)

    def test_scaffold_web_contracts(self):
        meta_web, body_web = scaffold_prompt(
            self.profile, "test-repo", "accessible-card", "WEB-ACCESSIBLE"
        )
        self.assertEqual(meta_web["framework"], "WEB-ACCESSIBLE")
        self.assertIn("## Semantic Landmark Hierarchy", body_web)
        self.assertIn("## Keyboard & ARIA State Contracts", body_web)

        meta_sec, body_sec = scaffold_prompt(
            self.profile, "test-repo", "secure-action", "DEFENSIVE-ACTION"
        )
        self.assertEqual(meta_sec["framework"], "DEFENSIVE-ACTION")
        self.assertIn("## Boundary Contract (Server Action)", body_sec)
        self.assertIn("## Runtime Schema (Zod)", body_sec)

    def test_scaffold_score_structure(self):
        meta, body = scaffold_prompt(
            self.profile,
            repo_name="py-service",
            prompt_name="add-auth",
            framework="RISEN",
        )
        self.assertIn("score", meta)
        self.assertIn("## Role", body)
        for key in [
            "clarity",
            "specificity",
            "context",
            "completeness",
            "structure",
            "cognitive",
            "overall",
        ]:
            self.assertIn(key, meta["score"])
            self.assertIsInstance(meta["score"][key], (int, float))


if __name__ == "__main__":
    unittest.main()
