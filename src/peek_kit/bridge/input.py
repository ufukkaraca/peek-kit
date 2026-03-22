import Quartz
from AppKit import NSEvent
import time
from typing import Tuple

def type_text(text: str, clear_first: bool = False) -> bool:
    """
    Types text by simulating keyboard events using Quartz (CGEvent).
    """
    if clear_first:
        press_key("cmd+a")
        time.sleep(0.1)
        press_key("delete")
        time.sleep(0.1)

    # Convert text to AppleScript keystrokes (most reliable non-C API method without generating 100 CG events manually)
    import subprocess
    escaped_text = text.replace('"', '\\"').replace("'", "\\'")
    script = f'tell application "System Events" to keystroke "{escaped_text}"'
    p = subprocess.run(['osascript', '-e', script], capture_output=True)
    return p.returncode == 0

def press_key(key_combo: str) -> bool:
    """
    Presses a key combo (e.g. 'cmd+z', 'return', 'tab')
    """
    keys = key_combo.lower().split('+')
    
    modifiers = []
    target_key = None
    
    for k in keys:
        if k in ('cmd', 'command'):
            modifiers.append("command down")
        elif k in ('shift',):
            modifiers.append("shift down")
        elif k in ('ctrl', 'control'):
            modifiers.append("control down")
        elif k in ('alt', 'option'):
            modifiers.append("option down")
        else:
            target_key = k

    if not target_key:
        return False

    # Map special keys to AppleScript terms
    special_key_map = {
        'return': 'return',
        'enter': 'return',
        'escape': 'escape',
        'tab': 'tab',
        'space': 'space',
        'delete': 'delete',
        'up': 'up arrow',
        'down': 'down arrow',
        'left': 'left arrow',
        'right': 'right arrow'
    }

    import subprocess
    script_lines = ['tell application "System Events"']
    
    if target_key in special_key_map:
        key_cmd = f"key code {getKeyCode(target_key)}" if getKeyCode(target_key) else f"keystroke {special_key_map[target_key]}"
    else:
        key_cmd = f'keystroke "{target_key}"'

    if modifiers:
        mod_str = "{" + ", ".join(modifiers) + "}"
        script_lines.append(f'{key_cmd} using {mod_str}')
    else:
        script_lines.append(key_cmd)
        
    script_lines.append('end tell')
    
    script = "\n".join(script_lines)
    p = subprocess.run(['osascript', '-e', script], capture_output=True)
    return p.returncode == 0

def getKeyCode(key_name: str):
    # Mapping for special key codes that keystroke doesn't handle well in AS
    mapping = {
        'escape': 53,
        'return': 36,
        'tab': 48,
        'space': 49,
        'delete': 51,
        'up': 126,
        'down': 125,
        'left': 123,
        'right': 124
    }
    return mapping.get(key_name)

def click_coordinates(x: int, y: int, click_type: str = 'single') -> bool:
    import pyautogui
    # Smoothly move to the coordinates to show intent to the user
    pyautogui.moveTo(x, y, duration=0.6, tween=pyautogui.easeInOutQuad)
    
    point = Quartz.CGPoint(x, y)
    event_down = Quartz.CGEventCreateMouseEvent(None, Quartz.kCGEventLeftMouseDown, point, Quartz.kCGMouseButtonLeft)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_down)
    
    time.sleep(0.05)
    
    # Left mouse up
    event_up = Quartz.CGEventCreateMouseEvent(None, Quartz.kCGEventLeftMouseUp, point, Quartz.kCGMouseButtonLeft)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_up)
    
    if click_type == 'double':
        time.sleep(0.1)
        Quartz.CGEventSetIntegerValueField(event_down, Quartz.kCGMouseEventClickState, 2)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_down)
        time.sleep(0.05)
        Quartz.CGEventSetIntegerValueField(event_up, Quartz.kCGMouseEventClickState, 2)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_up)

    return True
