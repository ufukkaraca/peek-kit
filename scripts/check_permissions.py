import sys
from peek_kit.utils.permissions import check_accessibility_permissions

if __name__ == "__main__":
    if check_accessibility_permissions(prompt=True):
        print("✅ Accessibility permission is granted.")
        sys.exit(0)
    else:
        print("❌ Accessibility permission is NOT granted.")
        print("Please enable it in System Settings > Privacy & Security > Accessibility.")
        print("Grant access to your terminal application, then run this check again.")
        sys.exit(1)
