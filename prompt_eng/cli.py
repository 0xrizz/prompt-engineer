"""Central CLI router for prompt-engineer hub."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import prompt_eng
from prompt_eng.models import (
    HarnessInfo,
    RepoProfile,
    StackInfo,
    dump_frontmatter_markdown,
    load_yaml_simple,
)
from prompt_eng.scanner import (
    save_repository_profile,
    scan_all_repositories,
    scan_repository,
)
from prompt_eng.studio.catalog import query_prompt_catalog
from prompt_eng.studio.diff import compare_prompt_diff
from prompt_eng.studio.linter import lint_prompt
from prompt_eng.studio.scaffolder import scaffold_prompt
from prompt_eng.studio.scorer import evaluate_rubric, render_rubric_table
from prompt_eng.transcripts.resolver import SessionResolver, render_session_summary_markdown


def _read_file_or_str(val: str) -> str:
    try:
        p = Path(val)
        if p.exists() and p.is_file():
            return p.read_text(encoding="utf-8")
    except (OSError, ValueError):  # fmt: skip
        pass
    return val


FRAMEWORK_CHOICES = [
    "risen",
    "costar",
    "co-star",
    "bab",
    "react",
    "got",
    "meta-prompting",
    "bot",
    "medprompt",
    "web-accessible",
    "defensive-action",
    "graph-of-thoughts",
    "buffer-of-thoughts",
]

_ALIAS_MAP = {
    "costar": "co-star",
    "metaprompting": "meta-prompting",
    "med-prompt": "medprompt",
    "web_accessible": "web-accessible",
    "defensive_action": "defensive-action",
    "graph-of-thoughts": "got",
    "graph_of_thoughts": "got",
    "buffer-of-thoughts": "bot",
    "buffer_of_thoughts": "bot",
}


def _normalize_framework(val: str) -> str:
    cleaned = val.strip().lower()
    return _ALIAS_MAP.get(cleaned, cleaned)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="prompt-eng",
        description="Centralized Prompt Engineering Studio & Multi-Repo Hub CLI",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"prompt-eng {prompt_eng.__version__}",
    )
    subparsers = parser.add_subparsers(dest="command", help="Studio commands")

    # scan command
    p_scan = subparsers.add_parser(
        "scan", help="Scan /home/rizz/dev/* repositories and generate profiles"
    )
    p_scan.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Specific repo name or path to scan (optional)",
    )
    p_scan.add_argument(
        "--repo",
        default=None,
        help="Specific repository name or path to scan",
    )
    p_scan.add_argument(
        "--root", default="/home/rizz/dev", help="Root directory containing target repos"
    )
    p_scan.add_argument(
        "--output", default=None, help="Output directory to store repo profiles (default: repos/)"
    )

    # transcript command
    p_trans = subparsers.add_parser("transcript", help="Extract and summarize session transcript")
    p_trans.add_argument("--repo", required=True, help="Target repository name")
    p_trans.add_argument("--session", help="Specific conversation ID or session name")
    p_trans.add_argument("--file", help="Explicit path to JSONL log file")
    p_trans.add_argument(
        "--format", choices=["md", "json"], default="md", help="Output format (md or json)"
    )

    # profile command
    p_prof = subparsers.add_parser("profile", help="Display profile for a target repository")
    p_prof.add_argument("repo", help="Repository name")

    # score command
    p_score = subparsers.add_parser("score", help="Evaluate prompt against 5-dimension rubric")
    p_score.add_argument("text", nargs="?", help="Prompt text to score")
    p_score.add_argument("--file", help="File containing prompt to score")

    # diff command
    p_diff = subparsers.add_parser("diff", help="Compare original vs optimized prompt")
    p_diff.add_argument("before", help="Path to original prompt file or string")
    p_diff.add_argument("after", help="Path to optimized prompt file or string")

    # list command
    subparsers.add_parser("list", help="List tracked repositories and prompts")

    # scaffold command
    p_scaffold = subparsers.add_parser(
        "scaffold", help="Generate prompt template from repo profile"
    )
    p_scaffold.add_argument("--repo", required=True, help="Target repository name")
    p_scaffold.add_argument("--name", required=True, help="Prompt name/slug")
    p_scaffold.add_argument(
        "--framework",
        "-f",
        choices=FRAMEWORK_CHOICES,
        type=_normalize_framework,
        default="risen",
        help="Prompt framework (SOTA reasoning: GoT, Meta-Prompting, BoT, Medprompt; Web contracts: Web-Accessible, Defensive-Action; Classic: RISEN, CO-STAR, BAB, ReAct)",
    )
    p_scaffold.add_argument(
        "--stdout",
        action="store_true",
        help="Print generated prompt to stdout instead of saving file",
    )

    # lint command
    p_lint = subparsers.add_parser(
        "lint", help="Lint prompt against repository invariants and framework rules"
    )
    p_lint.add_argument("target", help="Prompt text or file path to lint")
    p_lint.add_argument("--repo", required=True, help="Target repository name for invariant checks")
    p_lint.add_argument(
        "--framework",
        "-f",
        choices=FRAMEWORK_CHOICES,
        type=_normalize_framework,
        default="",
        help="Expected framework structure (SOTA reasoning: GoT, Meta-Prompting, BoT, Medprompt; Web contracts: Web-Accessible, Defensive-Action; Classic: RISEN, CO-STAR, BAB, ReAct)",
    )
    p_lint.add_argument("--strict", action="store_true", help="Fail on any warning (exit code 1)")

    # search command
    p_search = subparsers.add_parser("search", help="Search prompt catalog across repos")
    p_search.add_argument("query", nargs="?", default="", help="Keyword or framework to search")
    p_search.add_argument("--repo", default=None, help="Filter by repository name")
    p_search.add_argument("--framework", default=None, help="Filter by framework")
    p_search.add_argument(
        "--min-score", type=float, default=None, help="Filter by minimum overall score"
    )
    p_search.add_argument("--json", action="store_true", help="Output results in JSON format")

    # save-prompt command
    p_save = subparsers.add_parser("save-prompt", help="Save engineered prompt with frontmatter")
    p_save.add_argument("--repo", required=True, help="Target repo name")
    p_save.add_argument("--name", required=True, help="Prompt slug name")
    p_save.add_argument(
        "--framework", required=True, help="Prompt framework used (e.g. RISEN, CO-STAR)"
    )
    p_save.add_argument("--content", help="Prompt body string")
    p_save.add_argument("--file", help="File containing prompt body")

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0

    app_root = Path(__file__).resolve().parent.parent
    repos_dir = app_root / "repos"

    if args.command == "scan":
        dev_root = Path(args.root)
        out_repos_dir = Path(args.output) if args.output else repos_dir
        target_repo = args.repo or args.target

        if target_repo:
            target_path = Path(target_repo)
            if not target_path.is_absolute():
                if (dev_root / target_repo).exists():
                    target_path = dev_root / target_repo
                elif Path(target_repo).resolve().exists():
                    target_path = Path(target_repo).resolve()
                else:
                    target_path = dev_root / target_repo
            if not target_path.exists() or not target_path.is_dir():
                print(
                    f"Error: Target repository directory not found: {target_path}",
                    file=sys.stderr,
                )
                return 1

            profile = scan_repository(target_path)
            profile_file = save_repository_profile(profile, out_repos_dir)
            print(
                f"✓ Successfully scanned and updated profile for {profile.name} at {profile_file}"
            )
            return 0

        print(f"Scanning target repositories in {dev_root}...")
        profiles = scan_all_repositories(dev_root, out_repos_dir)
        print(
            f"✓ Successfully scanned and updated {len(profiles)} repository profiles in {out_repos_dir}/"
        )
        return 0

    if args.command == "transcript":
        file_path = Path(args.file) if args.file else None
        try:
            summary = SessionResolver.resolve_session(
                args.repo, session_id=args.session, file_path=file_path
            )
            if args.format == "json":
                import dataclasses
                import json

                print(json.dumps(dataclasses.asdict(summary), indent=2))
            else:
                print(render_session_summary_markdown(summary))
            return 0
        except Exception as e:  # noqa: BLE001
            print(f"Error resolving session: {e}", file=sys.stderr)
            return 1

    if args.command == "profile":
        prof_file = repos_dir / args.repo / "profile.yaml"
        if not prof_file.exists():
            print(
                f"Profile for '{args.repo}' not found. Run 'prompt-eng scan' first.",
                file=sys.stderr,
            )
            return 1
        print(prof_file.read_text(encoding="utf-8"))
        return 0

    if args.command == "score":
        text = args.text or ""
        if args.file:
            try:
                fp = Path(args.file)
                if fp.exists() and fp.is_file():
                    text = fp.read_text(encoding="utf-8")
            except (OSError, ValueError):  # fmt: skip
                pass
        if not text:
            print("Error: Must provide prompt text or --file", file=sys.stderr)
            return 1
        score = evaluate_rubric(text)
        print(render_rubric_table(score))
        return 0

    if args.command == "diff":
        b_text = _read_file_or_str(args.before)
        a_text = _read_file_or_str(args.after)
        print(compare_prompt_diff(b_text, a_text))
        return 0

    if args.command == "list":
        results = query_prompt_catalog(repos_dir, "")
        repo_names = (
            sorted([d.name for d in repos_dir.iterdir() if d.is_dir()])
            if repos_dir.exists()
            else []
        )
        print(f"=== Tracked Repositories ({len(repo_names)}) ===")
        for name in repo_names:
            p_count = (
                len(list((repos_dir / name / "prompts").glob("*.md")))
                if (repos_dir / name / "prompts").exists()
                else 0
            )
            print(f"- {name:<20} ({p_count} prompts)")
        print(f"\nTotal Prompts in Catalog: {len(results)}")
        return 0

    if args.command == "scaffold":
        profile_file = repos_dir / args.repo / "profile.yaml"
        profile = None
        if profile_file.exists():
            loaded = load_yaml_simple(profile_file.read_text(encoding="utf-8"))
            st = loaded.get("stack", {})
            ha = loaded.get("harness", {})
            profile = RepoProfile(
                name=loaded.get("name", args.repo),
                path=loaded.get("path", ""),
                description=loaded.get("description", ""),
                stack=StackInfo(
                    language=st.get("language", ""),
                    package_manager=st.get("package_manager", ""),
                    test_framework=st.get("test_framework", ""),
                    linter=st.get("linter", ""),
                ),
                harness=HarnessInfo(
                    instruction_files=ha.get("instruction_files", []),
                    active_skills=ha.get("active_skills", []),
                    rules=ha.get("rules", []),
                ),
                invariants=loaded.get("invariants", []),
                failure_gates=loaded.get("failure_gates", []),
                active_milestone=loaded.get("active_milestone", ""),
            )

        meta, body = scaffold_prompt(profile, args.repo, args.name, args.framework)
        rendered = dump_frontmatter_markdown(meta, body)
        if args.stdout:
            print(rendered)
            return 0

        target_dir = repos_dir / args.repo / "prompts"
        target_dir.mkdir(parents=True, exist_ok=True)
        slug = args.name if args.name.endswith(".md") else f"{args.name}.md"
        out_file = target_dir / slug
        out_file.write_text(rendered, encoding="utf-8")
        print(f"✓ Scaffolded {args.framework} prompt at {out_file}")
        return 0

    if args.command == "lint":
        text = _read_file_or_str(args.target)
        profile_file = repos_dir / args.repo / "profile.yaml"
        profile = None
        if profile_file.exists():
            loaded = load_yaml_simple(profile_file.read_text(encoding="utf-8"))
            st = loaded.get("stack", {})
            profile = RepoProfile(
                name=loaded.get("name", args.repo),
                path=loaded.get("path", ""),
                description=loaded.get("description", ""),
                stack=StackInfo(
                    language=st.get("language", ""),
                    package_manager=st.get("package_manager", ""),
                    test_framework=st.get("test_framework", ""),
                    linter=st.get("linter", ""),
                ),
                invariants=loaded.get("invariants", []),
                failure_gates=loaded.get("failure_gates", []),
            )

        report = lint_prompt(
            text,
            profile,
            framework=args.framework,
            prompt_name=args.target,
            strict=args.strict,
        )
        if not report.issues:
            print(f"✓ Lint passed: No issues found for '{args.target}'")
            return 0

        print(f"\n--- Lint Report: {args.target} ({report.repo}) ---")
        for issue in report.issues:
            color = "\033[31m" if issue.severity == "ERROR" else "\033[33m"
            print(f"{color}[{issue.severity}]\033[0m {issue.rule_id}: {issue.message}")
            if issue.suggestion:
                print(f"  ↳ Suggestion: {issue.suggestion}")
        print("--------------------------------------------------\n")

        if report.has_errors or (report.has_warnings and args.strict):
            return 1
        return 0

    if args.command == "search":
        matches = query_prompt_catalog(
            repos_dir,
            args.query,
            repo=args.repo,
            framework=args.framework,
            min_score=args.min_score,
        )
        if args.json:
            import json

            print(json.dumps(matches, indent=2))
            return 0

        print(f"Found {len(matches)} prompt(s) matching query:\n")
        for m in matches:
            print(f"[{m['repo']}] {m['file']} (FW: {m['framework']}, Score: {m['overall_score']})")
            print(f"  {m['preview']}\n")
        return 0

    if args.command == "save-prompt":
        body = args.content or ""
        if args.file:
            try:
                fp = Path(args.file)
                if fp.exists() and fp.is_file():
                    body = fp.read_text(encoding="utf-8")
            except (OSError, ValueError):  # fmt: skip
                pass
        if not body:
            print("Error: Must provide prompt content or --file", file=sys.stderr)
            return 1

        target_dir = repos_dir / args.repo / "prompts"
        target_dir.mkdir(parents=True, exist_ok=True)
        slug = args.name if args.name.endswith(".md") else f"{args.name}.md"
        out_file = target_dir / slug

        score = evaluate_rubric(body)
        meta = {
            "name": args.name,
            "repo": args.repo,
            "framework": args.framework,
            "score": {
                "clarity": score.clarity,
                "specificity": score.specificity,
                "context": score.context,
                "completeness": score.completeness,
                "structure": score.structure,
                "overall": score.overall,
            },
        }
        out_file.write_text(dump_frontmatter_markdown(meta, body), encoding="utf-8")
        print(f"✓ Saved engineered prompt to {out_file}")
        return 0

    return 0
