import AppKit
import time
import subprocess
from typing import List, Optional
from peek_kit.models.elements import AppInfo

def list_running_apps() -> List[AppInfo]:
    workspace = AppKit.NSWorkspace.sharedWorkspace()
    apps = workspace.runningApplications()
    
    result = []
    for app in apps:
        if app.activationPolicy() == AppKit.NSApplicationActivationPolicyRegular:
            bundle_id = app.bundleIdentifier()
            display_name = app.localizedName()
            is_frontmost = app.isActive()
            # Approximation of window count
            # A full implementation would query AXWindow, but this is a stub.
            # Electron check: very rudimentary.
            is_electron = False
            if bundle_id:
                is_electron = 'electron' in bundle_id.lower()
            
            result.append(AppInfo(
                pid=app.processIdentifier(),
                bundle_id=bundle_id or "",
                display_name=display_name or "",
                window_count=1,
                is_frontmost=is_frontmost,
                is_electron=is_electron
            ))
    return result

def launch_app(app_name: str, wait_seconds: int = 5) -> bool:
    workspace = AppKit.NSWorkspace.sharedWorkspace()
    url = workspace.URLForApplicationWithBundleIdentifier_(app_name)
    if not url:
        p = subprocess.run(['open', '-a', app_name], capture_output=True)
        time.sleep(wait_seconds)
        return p.returncode == 0
    
    config = AppKit.NSWorkspaceOpenConfiguration.configuration()
    workspace.openApplicationAtURL_configuration_completionHandler_(url, config, None)
    time.sleep(wait_seconds)
    return True

def focus_window(app_name: str, window_index: int = 0) -> bool:
    workspace = AppKit.NSWorkspace.sharedWorkspace()
    apps = workspace.runningApplications()
    for app in apps:
        if app.localizedName() == app_name or app.bundleIdentifier() == app_name:
            app.activateWithOptions_(AppKit.NSApplicationActivateIgnoringOtherApps)
            time.sleep(0.5)
            return True
    return False

def get_bundle_id(app_name: str) -> Optional[str]:
    workspace = AppKit.NSWorkspace.sharedWorkspace()
    apps = workspace.runningApplications()
    for app in apps:
        if app.localizedName() == app_name:
            return app.bundleIdentifier()
    return None
