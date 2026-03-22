from typing import Optional, List
from mcp.server.fastmcp import FastMCP
from peek_kit.models.actions import ActionResult, AppLaunchResult
from peek_kit.bridge.apps import launch_app as _launch_app, focus_window as _focus_window, get_bundle_id
from peek_kit.bridge.input import type_text as _type_text, press_key as _press_key, click_coordinates as _click_coordinates
from peek_kit.bridge.accessibility import click_element as _click_element
from peek_kit.bridge.menu import navigate_menu as _navigate_menu
import atomacos

def register_action_tools(mcp: FastMCP):
    @mcp.tool()
    def click_element(app_name: str, element_id: str, click_type: str = 'single') -> ActionResult:
        """Clicks an element identified by element_id from a previous tree extraction."""
        _focus_window(app_name)
        success = _click_element(element_id, click_type)
        return ActionResult(success=success, element_id=element_id, action_taken=f"click {click_type}")

    @mcp.tool()
    def click_coordinates(x: int, y: int, click_type: str = 'single') -> ActionResult:
        """Fallback click by screen coordinates."""
        success = _click_coordinates(x, y, click_type)
        return ActionResult(success=success, coordinates=(x,y), action_taken=f"click {click_type}")

    @mcp.tool()
    def type_text(text: str, clear_first: bool = False) -> ActionResult:
        """Types text into the currently focused element."""
        success = _type_text(text, clear_first)
        return ActionResult(success=success, text_typed=text, char_count=len(text), action_taken="type")

    @mcp.tool()
    def press_key(key: str) -> ActionResult:
        """Sends a key combination (e.g. 'return', 'cmd+z')."""
        success = _press_key(key)
        return ActionResult(success=success, key_sent=key, action_taken="press_key")

    @mcp.tool()
    def scroll(app_name: str, direction: str, element_id: Optional[str] = None, amount: int = 3) -> ActionResult:
        """Scrolls within a scrollable element or window."""
        # Simple applescript scroll hook
        # Down: negative scroll Y, Up: positive scroll Y in CGEvent
        import Quartz
        import time
        pixels = amount * 10
        if direction == "up":
            pixels = pixels
        elif direction == "down":
            pixels = -pixels
        else:
            return ActionResult(success=False, error_message="Only up and down are currently supported for generic scroll.", action_taken="scroll")
            
        event = Quartz.CGEventCreateScrollWheelEvent(None, Quartz.kCGScrollEventUnitPixel, 1, pixels)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
        time.sleep(0.1)
        return ActionResult(success=True, direction=direction, amount=amount, action_taken="scroll")

    @mcp.tool()
    def open_app(app_name: str, wait_seconds: int = 5) -> AppLaunchResult:
        """Launches an application by name or bundle ID and waits for it to be ready."""
        success = _launch_app(app_name, wait_seconds)
        bundle_id = get_bundle_id(app_name)
        return AppLaunchResult(success=success, bundle_id=bundle_id or app_name, display_name=app_name, pid=0, ready=success)

    @mcp.tool()
    def focus_window(app_name: str, window_index: int = 0) -> ActionResult:
        """Brings an app window to front and focuses it."""
        success = _focus_window(app_name, window_index)
        return ActionResult(success=success, action_taken="focus_window")

    @mcp.tool()
    def navigate_menu(app_name: str, path: List[str]) -> ActionResult:
        """Navigates a menu path."""
        _focus_window(app_name)
        success = _navigate_menu(app_name, path)
        return ActionResult(success=success, path_taken=path, action_taken="navigate_menu")
