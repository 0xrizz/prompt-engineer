"""Session resolver to find and format session transcripts."""

from __future__ import annotations

from pathlib import Path

from prompt_eng.models import SessionSummary

from .antigravity import parse_antigravity_transcript
from .claude import parse_claude_transcript


class SessionResolver:
    """Discovers and parses transcripts from Antigravity and Claude Code sessions."""

    @staticmethod
    def find_latest_session(
        repo_name: str,
        target_dir: Path | None = None,
    ) -> tuple[str, Path]:
        """Find the newest session transcript for a target repository or search directory."""
        # 1. If target_dir provided, scan strictly within it
        if target_dir is not None:
            if not target_dir.exists():
                raise FileNotFoundError(f"Target directory does not exist: {target_dir}")

            if target_dir.is_file():
                if "claude" in str(target_dir).lower():
                    return "claude-code", target_dir
                return "antigravity", target_dir

            # Check Antigravity pattern in target_dir
            ag_candidates = sorted(
                target_dir.glob("*/.system_generated/logs/transcript.jsonl"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if ag_candidates:
                return "antigravity", ag_candidates[0]

            direct_ag = sorted(
                target_dir.glob("**/transcript.jsonl"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if direct_ag:
                return "antigravity", direct_ag[0]

            # Check Claude JSONL files in target_dir
            cl_candidates = sorted(
                target_dir.glob("**/*.jsonl"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if cl_candidates:
                return "claude-code", cl_candidates[0]

            raise FileNotFoundError(f"No active session transcript found in: {target_dir}")

        # 2. Check standard Antigravity brain
        ag_brain = Path.home() / ".gemini" / "antigravity" / "brain"
        if ag_brain.exists():
            sessions = sorted(
                ag_brain.glob("*/.system_generated/logs/transcript.jsonl"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if sessions:
                return "antigravity", sessions[0]

        # 3. Check Claude projects directory
        claude_projects = Path.home() / ".claude" / "projects"
        if claude_projects.exists():
            cl_sessions = sorted(
                claude_projects.glob("**/*.jsonl"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if cl_sessions:
                return "claude-code", cl_sessions[0]

        raise FileNotFoundError(f"No active session transcript found for repo: {repo_name}")

    @staticmethod
    def resolve_session(
        repo_name: str,
        session_id: str | None = None,
        file_path: Path | None = None,
    ) -> SessionSummary:
        """Resolve a session by direct path, session ID, or latest detected transcript."""
        if file_path is not None:
            if not file_path.exists():
                raise FileNotFoundError(f"Transcript file not found: {file_path}")
            if "claude" in str(file_path).lower():
                return parse_claude_transcript(file_path, repo_name=repo_name)
            return parse_antigravity_transcript(file_path, repo_name=repo_name)

        if session_id is not None:
            home = Path.home()
            ag_brain = home / ".gemini" / "antigravity" / "brain"
            claude_projects = home / ".claude" / "projects"

            candidate = ag_brain / session_id / ".system_generated" / "logs" / "transcript.jsonl"
            if candidate.exists():
                return parse_antigravity_transcript(candidate, repo_name=repo_name)

            if claude_projects.exists():
                for cl_cand in claude_projects.glob(f"**/{session_id}.jsonl"):
                    if cl_cand.exists():
                        return parse_claude_transcript(cl_cand, repo_name=repo_name)

            raise FileNotFoundError(f"Session '{session_id}' not found for repo: {repo_name}")

        # Fallback to finding the latest session only when neither file_path nor session_id is passed
        harness, latest_path = SessionResolver.find_latest_session(repo_name)
        if harness == "claude-code":
            return parse_claude_transcript(latest_path, repo_name=repo_name)
        return parse_antigravity_transcript(latest_path, repo_name=repo_name)


def render_session_summary_markdown(summary: SessionSummary) -> str:
    """Render a SessionSummary dataclass into formatted markdown."""
    tools_list = (
        "\n".join(f"- `{t}`" for t in summary.key_tools) if summary.key_tools else "None recorded."
    )
    errors_list = (
        "\n".join(f"- `{e}`" for e in summary.errors) if summary.errors else "No errors detected."
    )

    return f"""## Session Context Summary
- **Target Repository**: {summary.repo_name}
- **Harness**: {summary.harness}
- **Session ID**: `{summary.session_id}`

### 🎯 Initial User Goal
{summary.user_goal}

### 🛠️ Key Tools & Commands Executed
{tools_list}

### ⚠️ Blockers & Errors
{errors_list}

### 💬 Latest Conversation Turn
{summary.last_turn_state}
"""
