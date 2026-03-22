from typing import List, Optional, Tuple, Any
from pydantic import BaseModel, Field

class Element(BaseModel):
    element_id: str
    role: str
    title: Optional[str] = None
    value: Optional[str] = None
    description: Optional[str] = None
    position: Optional[Tuple[float, float]] = None
    size: Optional[Tuple[float, float]] = None
    is_enabled: bool = True
    is_focused: bool = False
    children: List['Element'] = Field(default_factory=list)

class AccessibilityTree(BaseModel):
    app_name: str
    bundle_id: str
    root_element: Element
    element_count: int
    timestamp: str

class Screenshot(BaseModel):
    base64_png: str
    width: int
    height: int
    element_count: Optional[int] = None
    timestamp: str

class MenuItem(BaseModel):
    title: str
    shortcut: Optional[str] = None
    enabled: bool = True
    submenu: Optional['MenuTree'] = None

class Menu(BaseModel):
    title: str
    items: List[MenuItem] = Field(default_factory=list)

class MenuTree(BaseModel):
    menus: List[Menu] = Field(default_factory=list)

class AppInfo(BaseModel):
    pid: int
    bundle_id: str
    display_name: str
    window_count: int
    is_frontmost: bool
    is_electron: bool = False

Element.model_rebuild()
MenuItem.model_rebuild()
Menu.model_rebuild()
