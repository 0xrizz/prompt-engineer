"""Central CLI router for prompt-engineer hub."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import prompt_eng
from prompt_eng.models import dump_frontmatter_markdown
from prompt_eng.scanner import scan_all_repositories
from prompt_eng.studio.catalog import query_prompt_catalog
from prompt_eng.studio.diff import compare_prompt_diff
from prompt_eng.studio.scorer import evaluate_rubric, render_rubric_table
from prompt_eng.transcripts.resolver import SessionResolver, render_session_summary_markdown


def _read_file_or_str(val: str) -> str:
    try:
        p = Path(val)
        if p.exists() and p.is_file():
            return p.read_text(encoding="utf-8")
    except (OSError, ValueError):
        pass
    return val


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
        "--root", default="/home/rizz/dev", help="Root directory containing target repos"
    )

    # transcript command
    p_trans = subparsers.add_parser("transcript", help="Extract and summarize session transcript")
    p_trans.add_argument("--repo", required=True, help="Target repository name")
    p_trans.add_argument("--session", help="Specific conversation ID or session name")
    p_trans.add_argument("--file", help="Explicit path to JSONL log file")

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

    # search command
    p_search = subparsers.add_parser("search", help="Search prompt catalog across repos")
    p_search.add_argument("query", help="Keyword or framework to search")

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
        print(f"Scanning target repositories in {dev_root}...")
        profiles = scan_all_repositories(dev_root, repos_dir)
        print(
            f"✓ Successfully scanned and updated {len(profiles)} repository profiles in {repos_dir}/"
        )
        return 0

    if args.command == "transcript":
        file_path = Path(args.file) if args.file else None
        try:
            summary = SessionResolver.resolve_session(
                args.repo, session_id=args.session, file_path=file_path
            )
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
            except (OSError, ValueError):
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

    if args.command == "search":
        matches = query_prompt_catalog(repos_dir, args.query)
        print(f"Found {len(matches)} prompt(s) matching '{args.query}':\n")
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
            except (OSError, ValueError):
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
