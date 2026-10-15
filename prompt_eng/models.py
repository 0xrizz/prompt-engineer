"""Domain models and serialization utilities for prompt-engineer."""

from __future__ import annotations

import dataclasses
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class StackInfo:
    language: str = "unknown"
    package_manager: str = "unknown"
    test_framework: str = "unknown"
    linter: str = "unknown"


@dataclass
class HarnessInfo:
    instruction_files: list[str] = field(default_factory=list)
    active_skills: list[str] = field(default_factory=list)
    rules: list[str] = field(default_factory=list)


@dataclass
class RepoProfile:
    name: str
    path: str
    description: str = ""
    stack: StackInfo = field(default_factory=StackInfo)
    harness: HarnessInfo = field(default_factory=HarnessInfo)
    invariants: list[str] = field(default_factory=list)
    last_scanned: str = ""
    active_milestone: str = ""
    blueprints: list[str] = field(default_factory=list)
    inspired_corpus: dict[str, int] = field(default_factory=dict)
    failure_gates: list[str] = field(default_factory=list)


@dataclass
class SessionSummary:
    harness: str  # 'antigravity', 'claude-code'
    session_id: str
    repo_name: str
    user_goal: str
    key_tools: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    last_turn_state: str = ""


@dataclass
class RubricScore:
    clarity: float
    specificity: float
    context: float
    completeness: float
    structure: float
    cognitive: float | None = None
    overall: float | None = None

    def __post_init__(self) -> None:
        if self.overall is None:
            if self.cognitive is not None:
                self.overall = round(
                    (
                        self.clarity
                        + self.specificity
                        + self.context
                        + self.completeness
                        + self.structure
                        + self.cognitive
                    )
                    / 6.0,
                    1,
                )
            else:
                self.overall = round(
                    (
                        self.clarity
                        + self.specificity
                        + self.context
                        + self.completeness
                        + self.structure
                    )
                    / 5.0,
                    1,
                )


@dataclass
class PromptSpec:
    name: str
    repo: str
    framework: str
    target_harness: str
    session_id: str
    score: RubricScore
    content: str
    created_at: str


def dump_yaml_simple(data: dict[str, Any], indent: int = 0) -> str:
    """Lightweight zero-dependency YAML serializer for nested dictionaries and lists."""
    lines: list[str] = []
    prefix = " " * indent
    if dataclasses.is_dataclass(data):
        data = dataclasses.asdict(data)

    for key, value in data.items():
        if dataclasses.is_dataclass(value):
            value = dataclasses.asdict(value)

        if isinstance(value, dict):
            if not value:
                lines.append(f"{prefix}{key}: {{}}")
            else:
                lines.append(f"{prefix}{key}:")
                lines.append(dump_yaml_simple(value, indent + 2))
        elif isinstance(value, list):
            if not value:
                lines.append(f"{prefix}{key}: []")
            else:
                lines.append(f"{prefix}{key}:")
                for item in value:
                    if dataclasses.is_dataclass(item):
                        item = dataclasses.asdict(item)
                    if isinstance(item, dict):
                        nested = dump_yaml_simple(item, indent + 4)
                        lines.append(f"{prefix}  - " + nested.lstrip())
                    elif isinstance(item, str):
                        special_starts = (
                            "-",
                            "#",
                            "@",
                            "!",
                            "*",
                            "&",
                            "|",
                            ">",
                            "%",
                            "?",
                            "[",
                            "{",
                            '"',
                            "'",
                        )
                        if ": " in item or item.endswith(":") or item.startswith(special_starts):
                            escaped = item.replace("\\", "\\\\").replace('"', '\\"')
                            lines.append(f'{prefix}  - "{escaped}"')
                        else:
                            lines.append(f"{prefix}  - {item}")
                    else:
                        lines.append(f"{prefix}  - {item}")
        else:
            if value is None:
                val_str = "null"
            elif isinstance(value, bool):
                val_str = "true" if value else "false"
            else:
                val_str = str(value)
            lines.append(f"{prefix}{key}: {val_str}")
    return "\n".join(lines)


def _parse_scalar(val: str) -> Any:
    val = val.strip()
    if not val:
        return ""
    if val in ("null", "None", "~"):
        return None
    if val.lower() == "true":
        return True
    if val.lower() == "false":
        return False
    if val == "[]":
        return []
    if val == "{}":
        return {}
    if val.startswith('"') and val.endswith('"'):
        return val[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if val.startswith("'") and val.endswith("'"):
        return val[1:-1]
    try:
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError:
        pass
    return val


def load_yaml_simple(yaml_str: str) -> dict[str, Any]:
    """Lightweight zero-dependency YAML parser for nested dictionaries and lists."""
    result: dict[str, Any] = {}
    lines = yaml_str.splitlines()
    stack: list[tuple[int, Any]] = [(-1, result)]

    def peek_next(idx: int) -> tuple[int | None, str | None]:
        for j in range(idx + 1, len(lines)):
            s = lines[j].strip()
            if s and not s.startswith("#"):
                ind = len(lines[j]) - len(lines[j].lstrip())
                return ind, s
        return None, None

    for i, line in enumerate(lines):
        if not line.strip() or line.strip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        while len(stack) > 1 and stack[-1][0] >= indent:
            stack.pop()

        current = stack[-1][1]

        if stripped.startswith("- "):
            item_str = stripped[2:].strip()
            if (item_str.startswith('"') and item_str.endswith('"')) or (
                item_str.startswith("'") and item_str.endswith("'")
            ):
                if isinstance(current, list):
                    current.append(_parse_scalar(item_str))
            elif ": " in item_str or item_str.endswith(":"):
                if ": " in item_str:
                    k, v = item_str.split(": ", 1)
                    item = {k.strip(): _parse_scalar(v)}
                else:
                    k = item_str[:-1].strip()
                    item = {k: None}
                if isinstance(current, list):
                    current.append(item)
                    stack.append((indent, item))
            else:
                if isinstance(current, list):
                    current.append(_parse_scalar(item_str))
        elif ":" in stripped:
            key, val = stripped.split(":", 1)
            key = key.strip()
            val = val.strip()
            if not val:
                next_ind, next_str = peek_next(i)
                if next_ind is not None and next_ind > indent:
                    if next_str and next_str.startswith("- "):
                        new_container: Any = []
                    else:
                        new_container = {}
                    if isinstance(current, dict):
                        current[key] = new_container
                    stack.append((indent, new_container))
                else:
                    if isinstance(current, dict):
                        current[key] = None
            else:
                parsed_val = _parse_scalar(val)
                if isinstance(current, dict):
                    current[key] = parsed_val
                elif isinstance(current, list) and current and isinstance(current[-1], dict):
                    current[-1][key] = parsed_val

    return result


def dump_frontmatter_markdown(meta: dict[str, Any], body: str) -> str:
    """Serialize frontmatter dict and markdown body into YAML frontmatter markdown."""
    yaml_part = dump_yaml_simple(meta)
    return f"---\n{yaml_part}\n---\n\n{body.strip()}\n"


def parse_frontmatter_markdown(text: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter markdown into metadata dict and body string."""
    if not text.startswith("---"):
        return {}, text
    match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n?(.*)$", text, re.DOTALL)
    if match:
        meta_str = match.group(1).strip()
        body_str = match.group(2)
        meta = load_yaml_simple(meta_str)
        return meta, body_str
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta_str = parts[1].strip()
    body_str = parts[2].strip()
    meta = load_yaml_simple(meta_str)
    return meta, body_str


@dataclass
class LintIssue:
    severity: str  # "ERROR" | "WARNING"
    rule_id: str
    message: str
    suggestion: str = ""


@dataclass
class LintReport:
    repo: str
    prompt_name: str
    is_valid: bool
    issues: list[LintIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "ERROR" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == "WARNING" for i in self.issues)
