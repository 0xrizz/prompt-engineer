"""Parser for Claude Code JSONL/session transcripts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from prompt_eng.models import SessionSummary


def parse_claude_transcript(jsonl_path: Path, repo_name: str = "") -> SessionSummary:
    """Parse Claude Code JSONL transcript into a SessionSummary."""
    if not jsonl_path.exists():
        raise FileNotFoundError(f"Claude transcript not found: {jsonl_path}")

    user_goal = ""
    tools: list[str] = []
    errors: list[str] = []
    last_turn_state = ""
    session_id = jsonl_path.stem

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry: dict[str, Any] = json.loads(line)
            except json.JSONDecodeError:
                continue

            role = entry.get("role") or entry.get("type", "")
            raw_content = entry.get("content", "")

            # Flatten content to string if structured
            if isinstance(raw_content, list):
                extracted_texts: list[str] = []
                for block in raw_content:
                    if isinstance(block, dict):
                        if block.get("type") == "text":
                            extracted_texts.append(block.get("text", ""))
                        elif block.get("type") == "tool_use":
                            tool_name = block.get("name") or "claude_tool_invocation"
                            tools.append(tool_name)
                    elif isinstance(block, str):
                        extracted_texts.append(block)
                content = "\n".join(extracted_texts)
            else:
                content = str(raw_content)

            if entry.get("type") == "tool_use":
                tool_name = entry.get("name") or "claude_tool_invocation"
                tools.append(tool_name)

            if role == "user" and not user_goal:
                user_goal = content.strip()

            if any(w in content.lower() for w in ["error", "fatal", "failed"]):
                snippet = content.strip().split("\n")[0][:120]
                errors.append(snippet)

            if role == "assistant" and content:
                last_turn_state = content.strip()[:300]

    return SessionSummary(
        harness="claude-code",
        session_id=session_id,
        repo_name=repo_name,
        user_goal=user_goal or "No explicit user goal recorded",
        key_tools=tools[-10:],
        errors=errors[-5:],
        last_turn_state=last_turn_state,
    )
