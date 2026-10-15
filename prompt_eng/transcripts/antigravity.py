"""Parser for Antigravity / agy / Antigravity IDE JSONL transcript logs."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from prompt_eng.models import SessionSummary


def _clean_user_input(text: str) -> str:
    """Extract core intent from <USER_REQUEST> if present, removing harness metadata."""
    req_match = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", text, re.DOTALL)
    if req_match:
        return req_match.group(1).strip()
    # Strip metadata blocks if present without user request tag
    cleaned = re.sub(
        r"<(ADDITIONAL_METADATA|USER_SETTINGS_CHANGE|SKILL)>.*?</\1>",
        "",
        text,
        flags=re.DOTALL,
    )
    return cleaned.strip()


def _extract_session_id(jsonl_path: Path) -> str:
    """Extract session ID from path convention or stem."""
    resolved = jsonl_path.resolve()
    parts = resolved.parts
    # Pattern: .../<session_id>/.system_generated/logs/transcript*.jsonl
    if len(parts) >= 4 and parts[-2] == "logs" and parts[-3] == ".system_generated":
        return parts[-4]
    return jsonl_path.stem


def parse_antigravity_transcript(jsonl_path: Path, repo_name: str = "") -> SessionSummary:
    """Parse Antigravity JSONL transcript into a SessionSummary."""
    if not jsonl_path.exists():
        raise FileNotFoundError(f"Transcript file not found: {jsonl_path}")

    user_goal = ""
    tools: list[str] = []
    errors: list[str] = []
    last_turn_state = ""
    session_id = _extract_session_id(jsonl_path)

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry: dict[str, Any] = json.loads(line)
            except json.JSONDecodeError:
                continue

            entry_type = entry.get("type", "")
            content = entry.get("content", "")

            if entry_type == "USER_INPUT" and not user_goal:
                user_goal = _clean_user_input(str(content))

            if "tool_calls" in entry and isinstance(entry["tool_calls"], list):
                for tc in entry["tool_calls"]:
                    if isinstance(tc, dict):
                        action = (
                            tc.get("toolAction")
                            or tc.get("toolSummary")
                            or tc.get("name")
                            or "tool_call"
                        )
                        tools.append(str(action))
                    else:
                        tools.append(str(tc))

            if entry_type == "TOOL_RESPONSE" and any(
                w in str(content).lower() for w in ["fail", "error", "traceback"]
            ):
                snippet = str(content).strip().split("\n")[0][:120]
                errors.append(snippet)

            if entry_type == "PLANNER_RESPONSE":
                text_content = str(content).strip() if content else ""
                if not text_content and "thinking" in entry and entry["thinking"]:
                    text_content = str(entry["thinking"]).strip()
                if text_content:
                    last_turn_state = text_content[:300]

    return SessionSummary(
        harness="antigravity",
        session_id=session_id,
        repo_name=repo_name,
        user_goal=user_goal or "No explicit user goal recorded",
        key_tools=tools[-10:],
        errors=errors[-5:],
        last_turn_state=last_turn_state,
    )
