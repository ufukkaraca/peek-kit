import asyncio
import subprocess
import time
from typing import Optional
from mcp.server.fastmcp import FastMCP
from rich.console import Console
from rich.panel import Panel
from peek_kit.models.actions import HumanActionResult, ResumeResult, AuthStateResult
from peek_kit.bridge.accessibility import extract_tree
from peek_kit.utils.auth_detection import is_auth_wall

# Global State for Human Handoff
_resume_event = asyncio.Event()
_user_note: Optional[str] = None
_timeout_expired = False
console = Console(stderr=True)

def get_timeout_expired() -> bool:
    return _timeout_expired

def register_human_tools(mcp: FastMCP):
    @mcp.tool(structured_output=False)
    async def request_human_action(reason: str, action_needed: str, timeout_seconds: int = 300) -> HumanActionResult:
        """Pause analysis and prompt user with a specific action needed."""
        global _resume_event, _user_note, _timeout_expired
        _resume_event.clear()
        _user_note = None
        _timeout_expired = False

        # 1. Print pause block to stdout
        message = f"Reason: {reason}\nAction Needed: {action_needed}\n\nType 'resume' within Claude Code once completed."
        panel = Panel(message, title="[yellow]Human Action Requested[/yellow]", border_style="yellow")
        console.print(panel)

        # 2. Play sound
        subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'])

        # 3. Block on asyncio.Event
        start_time = time.time()
        try:
            if timeout_seconds > 0:
                await asyncio.wait_for(_resume_event.wait(), timeout=timeout_seconds)
            else:
                await _resume_event.wait()
            resumed = True
        except asyncio.TimeoutError:
            _timeout_expired = True
            resumed = False

        waited_seconds = int(time.time() - start_time)
        return HumanActionResult(resumed=resumed, waited_seconds=waited_seconds, user_note=_user_note)

    @mcp.tool(structured_output=False)
    async def resume_analysis(note: Optional[str] = None) -> ResumeResult:
        """Resume after human completes the requested action."""
        global _resume_event, _user_note
        _user_note = note
        _resume_event.set()
        return ResumeResult(success=True, note_received=bool(note))

    @mcp.tool(structured_output=False)
    def check_auth_state(app_name: str, expected_state: str) -> AuthStateResult:
        """Verify auth wall is cleared before continuing exploration."""
        tree = extract_tree(app_name)
        # Check if auth wall heuristic still applies
        auth_type = is_auth_wall(tree)
        auth_cleared = auth_type is None

        # Generically provide the frontmost elements to help claude evaluate state
        summary = f"Root title: {tree.root_element.title}. Element count: {tree.element_count}. Auth detected: {auth_type}"
        return AuthStateResult(auth_wall_cleared=auth_cleared, current_screen_summary=summary)
