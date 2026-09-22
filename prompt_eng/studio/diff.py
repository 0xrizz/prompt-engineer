"""Terminal diff comparator showing changes between original and improved prompt."""

from __future__ import annotations

import difflib


def compare_prompt_diff(before: str, after: str) -> str:
    """Compare two prompts and return unified diff with ANSI terminal color codes."""
    before_lines = before.splitlines(keepends=True)
    after_lines = after.splitlines(keepends=True)
    diff = difflib.unified_diff(
        before_lines, after_lines, fromfile="Original Prompt", tofile="Optimized Prompt"
    )

    result = []
    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            result.append(f"\033[32m{line.rstrip()}\033[0m")  # Green
        elif line.startswith("-") and not line.startswith("---"):
            result.append(f"\033[31m{line.rstrip()}\033[0m")  # Red
        elif line.startswith("@@"):
            result.append(f"\033[36m{line.rstrip()}\033[0m")  # Cyan
        else:
            result.append(line.rstrip())
    return "\n".join(result)
