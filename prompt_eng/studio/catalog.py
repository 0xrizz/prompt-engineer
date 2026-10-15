"""Cross-repo prompt catalog query engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from prompt_eng.models import parse_frontmatter_markdown


def query_prompt_catalog(
    repos_dir: Path,
    query: str,
    repo: str | None = None,
    framework: str | None = None,
    min_score: float | None = None,
) -> list[dict[str, Any]]:
    """Search for prompts across all repo prompt catalogs matching query and structured filters."""
    matches: list[dict[str, Any]] = []
    q = query.lower()

    if not repos_dir.exists():
        return matches

    for repo_dir in sorted(repos_dir.iterdir(), key=lambda p: p.name):
        if not repo_dir.is_dir():
            continue
        if repo and repo.lower() not in repo_dir.name.lower():
            continue

        prompts_dir = repo_dir / "prompts"
        if not prompts_dir.exists():
            continue

        for p_file in sorted(prompts_dir.glob("*.md"), key=lambda p: p.name):
            try:
                content = p_file.read_text(encoding="utf-8", errors="ignore")
                meta, body = parse_frontmatter_markdown(content)
                prompt_fw = str(meta.get("framework", "N/A"))
                if framework and framework.lower() not in prompt_fw.lower():
                    continue

                score_meta = meta.get("score")
                overall_score: float | str = (
                    score_meta.get("overall", "N/A") if isinstance(score_meta, dict) else "N/A"
                )
                if min_score is not None and (
                    not isinstance(overall_score, (int, float)) or overall_score < min_score
                ):
                    continue

                haystack = f"{repo_dir.name} {p_file.name} {meta} {body}".lower()
                if q in haystack or not q:
                    matches.append(
                        {
                            "repo": repo_dir.name,
                            "file": p_file.name,
                            "path": str(p_file),
                            "framework": prompt_fw,
                            "overall_score": overall_score,
                            "preview": body.strip()[:100] + "...",
                        }
                    )
            except (OSError, ValueError, TypeError, KeyError):  # fmt: skip
                continue

    return matches
