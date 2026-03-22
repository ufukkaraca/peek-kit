import hashlib
import time
from typing import Dict, Any, Optional, Tuple, List
import atomacos
from peek_kit.models.elements import Element, AccessibilityTree
from peek_kit.utils.retry import retry_ax_call
from peek_kit.bridge.apps import get_bundle_id

_element_cache: Dict[str, Any] = {}

def _generate_element_id(bundle_id: str, role: str, title: str, position: Tuple[float, float]) -> str:
    s = f"{bundle_id}|{role}|{title}|{position[0]},{position[1]}"
    return hashlib.md5(s.encode('utf-8')).hexdigest()[:8]

@retry_ax_call(retries=3, backoff=0.3)
def extract_tree(app_name: str, max_depth: int = 8, include_invisible: bool = False) -> AccessibilityTree:
    bundle_id = get_bundle_id(app_name) or app_name
    app_ref = atomacos.getAppRefByLocalizedName(app_name)
    if not app_ref:
        raise Exception(f"Application {app_name} not found or not running.")
        
    global _element_cache
    _element_cache.clear()
    
    element_count = 0

    def traverse(ax_element: Any, depth: int) -> Optional[Element]:
        nonlocal element_count
        if depth > max_depth:
            return None
            
        try:
            role = getattr(ax_element, "AXRole", None)
            if not role:
                return None
                
            def safe_get(attr, default=None):
                try:
                    val = getattr(ax_element, attr, default)
                    return val if val is not None else default
                except Exception:
                    return default
                    
            size = safe_get("AXSize")
            pos = safe_get("AXPosition")
            
            # Simple visibility check (size > 0)
            if not include_invisible and size and (size.width <= 0 or size.height <= 0):
                return None
                
            title = safe_get("AXTitle")
            if isinstance(title, str) and not title:
                title = safe_get("AXDescription", "")
                
            value = safe_get("AXValue")
            desc = safe_get("AXDescription")
            is_enabled = safe_get("AXEnabled", True)
            is_focused = safe_get("AXFocused", False)
            
            pos_tuple = (pos.x, pos.y) if pos else (0, 0)
            size_tuple = (size.width, size.height) if size else (0, 0)
            
            el_id = _generate_element_id(bundle_id, str(role), str(title or ""), pos_tuple)
            _element_cache[el_id] = ax_element
            
            children_ax = ax_element.AXChildren or []
            parsed_children = []
            for c in children_ax:
                parsed_c = traverse(c, depth + 1)
                if parsed_c:
                    parsed_children.append(parsed_c)
                    
            el = Element(
                element_id=el_id,
                role=str(role),
                title=str(title) if title else None,
                value=str(value) if value else None,
                description=str(desc) if desc else None,
                position=pos_tuple,
                size=size_tuple,
                is_enabled=bool(is_enabled),
                is_focused=bool(is_focused),
                children=parsed_children
            )
            element_count += 1
            return el
        except Exception:
            # Skip unparseable elements
            return None

    root_el = traverse(app_ref, 0)
    if not root_el:
        raise Exception("Failed to extract accessibility tree root.")
        
    return AccessibilityTree(
        app_name=app_name,
        bundle_id=bundle_id,
        root_element=root_el,
        element_count=element_count,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    )

@retry_ax_call(retries=3, backoff=0.3)
def click_element(element_id: str, click_type: str = 'single') -> bool:
    if element_id not in _element_cache:
        raise Exception(f"Element {element_id} not found in cache. Extract tree first.")
        
    ax_el = _element_cache[element_id]
    
    # Visually move mouse to the element center before interacting
    try:
        import pyautogui
        pos = getattr(ax_el, "AXPosition", None)
        size = getattr(ax_el, "AXSize", None)
        if pos and size:
            target_x = pos.x + (size.width / 2)
            target_y = pos.y + (size.height / 2)
            pyautogui.moveTo(target_x, target_y, duration=0.6, tween=pyautogui.easeInOutQuad)
    except Exception:
        pass # Fallback cleanly if positioning fails

    if click_type == 'single' and 'AXPress' in ax_el.AXActionNames:
        ax_el.AXPress()
        return True
    elif click_type == 'single':
        # Fallback to mouse click via atomacos
        ax_el.clickMouseButtonLeft()
        return True
    elif click_type == 'right':
        ax_el.clickMouseButtonRight()
        return True
    elif click_type == 'double':
        ax_el.doubleClickMouse()
        return True
        
    return False

def find_elements_in_tree(tree: AccessibilityTree, role: Optional[str] = None, text: Optional[str] = None, enabled_only: bool = True) -> List[Element]:
    results = []
    
    def search(el: Element):
        match = True
        if role and role not in el.role:
            match = False
        if text:
            el_text = f"{el.title} {el.value} {el.description}".lower()
            if text.lower() not in el_text:
                match = False
        if enabled_only and not el.is_enabled:
            match = False
            
        if match:
            results.append(el)
            
        for child in el.children:
            search(child)
            
    search(tree.root_element)
    return results
