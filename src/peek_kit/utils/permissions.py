import sys
from ApplicationServices import AXIsProcessTrusted, AXIsProcessTrustedWithOptions
import CoreFoundation

def check_accessibility_permissions(prompt: bool = False) -> bool:
    """
    Check if the process is trusted for macOS Accessibility.
    If prompt=True, macOS will show the permission dialog if not already trusted.
    """
    if prompt:
        options = {CoreFoundation.kCFStringCreateWithCString(None, b"AXTrustedCheckOptionPrompt", 0): True}
        return AXIsProcessTrustedWithOptions(options)
    return AXIsProcessTrusted()

def require_accessibility():
    if not check_accessibility_permissions():
        # Use stderr to avoid corrupting MCP stdio transport on stdout
        print("Accessibility permission is required to run peek-kit.", file=sys.stderr)
        print("Please enable it in System Settings > Privacy & Security > Accessibility.", file=sys.stderr)
        print("Grant access to your terminal application (e.g. Terminal, iTerm2).", file=sys.stderr)
        sys.exit(1)

def check_all_permissions() -> dict:
    import builtins
    auth_status = {"accessibility": False, "screen_recording": False}
    
    # 1. Accessibility
    auth_status["accessibility"] = check_accessibility_permissions()
    
    # 2. Screen recording
    try:
        import Quartz
        window_list = Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID)
        # If we can see the "name" of other application windows like Dock, we have permission.
        has_name = False
        if window_list:
            for window in window_list:
                owner = window.get('kCGWindowOwnerName', '')
                name = window.get('kCGWindowName')
                if owner == 'Dock' and name is not None:
                    has_name = True
                    break
            # As a fallback if Dock window name is empty, just check if ANY window has a name
            if not has_name:
                 for window in window_list:
                     if window.get('kCGWindowName'):
                         has_name = True
                         break
        auth_status["screen_recording"] = has_name
    except Exception:
        auth_status["screen_recording"] = False

    return auth_status
