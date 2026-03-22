import re
from peek_kit.models.elements import AccessibilityTree
from enum import Enum
from typing import Optional

class AuthWallType(Enum):
    LOGIN = "login"
    SIGNUP = "signup"
    PAYWALL = "paywall"
    TWO_FACTOR = "two_factor"

def is_auth_wall(tree: AccessibilityTree) -> Optional[AuthWallType]:
    """
    Detects if the current screen is an auth wall based on specific heuristics.
    """
    has_secure_text_field = False
    
    auth_button_pattern = re.compile(r'sign.?in|log.?in|continue with|create account', re.IGNORECASE)
    auth_title_pattern = re.compile(r'login|sign in|welcome back|create your account', re.IGNORECASE)

    has_auth_button = False
    has_auth_title = False
    social_auth_count = 0

    def traverse(element):
        nonlocal has_secure_text_field, has_auth_button, has_auth_title, social_auth_count
        if element.role == "AXSecureTextField":
            has_secure_text_field = True
        
        if element.role == "AXButton" and element.title and auth_button_pattern.search(element.title):
            has_auth_button = True
            
        if element.role == "AXButton" and element.title and any(kw in element.title.lower() for kw in ["google", "apple", "github", "microsoft"]):
            social_auth_count += 1
            
        for child in element.children:
            traverse(child)

    traverse(tree.root_element)

    if tree.root_element.title and auth_title_pattern.search(tree.root_element.title):
        has_auth_title = True

    # If it's a very sparse screen (e.g. fewer than 10 elements) and has auth elements
    sparse = tree.element_count < 15

    if has_secure_text_field:
        if has_auth_button or has_auth_title or sparse:
            return AuthWallType.LOGIN
            
    if social_auth_count > 0 and sparse:
        return AuthWallType.LOGIN
        
    return None
