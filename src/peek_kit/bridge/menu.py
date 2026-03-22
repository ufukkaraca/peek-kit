import atomacos
from typing import List
from peek_kit.models.elements import MenuTree, Menu, MenuItem
from peek_kit.utils.retry import retry_ax_call

@retry_ax_call(retries=3, backoff=0.3)
def get_menu_structure(app_name: str) -> MenuTree:
    app_ref = atomacos.getAppRefByLocalizedName(app_name)
    if not app_ref:
        raise Exception(f"Application {app_name} not found or not running.")
        
    menu_bar = app_ref.AXMenuBar
    if not menu_bar:
        raise Exception("Menu bar not found for the application.")
        
    menus = []
    
    # Each top-level item in the menu bar is a menu (e.g., Apple, File, Edit)
    for top_level in menu_bar.AXChildren:
        title = top_level.AXTitle
        if not title:
            continue
            
        items = []
        if top_level.AXChildren and top_level.AXChildren[0].AXRole == 'AXMenu':
            dropdown = top_level.AXChildren[0]
            for item in dropdown.AXChildren:
                if item.AXRole == 'AXMenuItem':
                    item_title = item.AXTitle
                    if not item_title: continue
                    enabled = item.AXEnabled
                    shortcut = item.AXMenuItemCmdChar
                    
                    # Optional: Parse submenus, keeping it simple for now (1 level deep)
                    sub = None
                    if item.AXChildren and item.AXChildren[0].AXRole == 'AXMenu':
                        sub_tree = MenuTree()
                        # Recursively extracting submenu can cause infinite loops or take too long,
                        # skipping deep submenus for simplicity unless perfectly defined.
                        pass
                        
                    items.append(MenuItem(
                        title=item_title,
                        shortcut=shortcut,
                        enabled=enabled,
                        submenu=sub
                    ))
                    
        menus.append(Menu(title=title, items=items))
        
    return MenuTree(menus=menus)

@retry_ax_call(retries=3, backoff=0.3)
def navigate_menu(app_name: str, path: List[str]) -> bool:
    app_ref = atomacos.getAppRefByLocalizedName(app_name)
    if not app_ref:
        return False
        
    menu_bar = app_ref.AXMenuBar
    if not menu_bar:
        return False
        
    current_level = menu_bar
    for i, step in enumerate(path):
        found = False
        for child in current_level.AXChildren:
            if child.AXTitle == step:
                # If it's a top-level menu item with a submenu, we need to look into its AXMenu child
                if child.AXRole == 'AXMenuBarItem' and child.AXChildren:
                    current_level = child.AXChildren[0]
                elif child.AXRole == 'AXMenuItem':
                    if i == len(path) - 1:
                        # Final item, click it
                        if 'AXPress' in child.AXActionNames:
                            child.AXPress()
                            return True
                    elif child.AXChildren:
                        current_level = child.AXChildren[0]
                found = True
                break
        if not found:
            return False
            
    return False
