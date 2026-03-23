from typing import List, Optional
from mcp.server.fastmcp import FastMCP
from peek_kit.models.elements import AppInfo, AccessibilityTree, Screenshot, MenuTree, Element
from peek_kit.models.actions import AppState
from peek_kit.bridge.apps import list_running_apps as _list_running_apps
from peek_kit.bridge.accessibility import extract_tree, find_elements_in_tree
from peek_kit.bridge.screenshot import take_screenshot as _take_screenshot
from peek_kit.bridge.menu import get_menu_structure as _get_menu_structure

def register_perception_tools(mcp: FastMCP):
    @mcp.tool(structured_output=False)
    def get_peek_kit_version() -> str:
        """Returns the current installed version of peek-kit."""
        from importlib.metadata import version, PackageNotFoundError
        try:
            return version("peek-kit")
        except PackageNotFoundError:
            return "unknown"

    @mcp.tool(structured_output=False)
    def check_system_permissions() -> dict:
        """Checks if the MCP server has macOS Accessibility and Screen Recording permissions."""
        from peek_kit.utils.permissions import check_all_permissions
        return check_all_permissions()

    @mcp.tool(structured_output=False)
    def list_running_apps() -> List[AppInfo]:
        """List all currently running apps with their bundle IDs and window counts."""
        return _list_running_apps()

    @mcp.tool(structured_output=False)
    def get_accessibility_tree(app_name: str, max_depth: int = 8, include_invisible: bool = False) -> AccessibilityTree:
        """Extracts the full accessibility element hierarchy for the target application."""
        return extract_tree(app_name, max_depth, include_invisible)

    @mcp.tool(structured_output=False)
    def take_screenshot(app_name: str, annotated: bool = True, window_index: int = 0) -> Screenshot:
        """Captures the current state of the target app window."""
        tree = extract_tree(app_name) if annotated else None
        res = _take_screenshot(app_name, annotated, tree)
        if not res:
            raise Exception("Failed to take screenshot.")
        return res

    @mcp.tool(structured_output=False)
    def get_menu_structure(app_name: str) -> MenuTree:
        """Enumerates the full menu bar hierarchy for the application."""
        return _get_menu_structure(app_name)

    @mcp.tool(structured_output=False)
    def get_current_state(app_name: str) -> AppState:
        """Returns accessibility tree + annotated screenshot in one call."""
        tree = extract_tree(app_name)
        screenshot = _take_screenshot(app_name, annotated=True, tree=tree)
        if not screenshot:
            raise Exception("Failed to capture screenshot for state.")
        return AppState(tree=tree, screenshot=screenshot)

    @mcp.tool(structured_output=False)
    def find_elements(app_name: str, role: Optional[str] = None, text: Optional[str] = None, enabled_only: bool = True) -> List[Element]:
        """Searches the accessibility tree for elements matching a query."""
        tree = extract_tree(app_name)
        return find_elements_in_tree(tree, role, text, enabled_only)
