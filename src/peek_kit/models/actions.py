from typing import Optional, Tuple, Dict, List
from pydantic import BaseModel
from peek_kit.models.elements import AccessibilityTree, Screenshot

class ActionResult(BaseModel):
    success: bool
    element_id: Optional[str] = None
    coordinates: Optional[Tuple[int, int]] = None
    action_taken: str
    error_message: Optional[str] = None
    text_typed: Optional[str] = None
    char_count: Optional[int] = None
    key_sent: Optional[str] = None
    direction: Optional[str] = None
    amount: Optional[int] = None
    path_taken: Optional[List[str]] = None
    final_item_enabled: Optional[bool] = None

class AppState(BaseModel):
    tree: AccessibilityTree
    screenshot: Screenshot

class HumanActionResult(BaseModel):
    resumed: bool
    waited_seconds: int
    user_note: Optional[str] = None

class AppLaunchResult(BaseModel):
    success: bool
    bundle_id: str
    display_name: str
    pid: int
    ready: bool

class AuthStateResult(BaseModel):
    auth_wall_cleared: bool
    current_screen_summary: str

class ResumeResult(BaseModel):
    success: bool
    note_received: bool

class ReportResult(BaseModel):
    success: bool
    filepaths: Dict[str, str]
    word_count: int
    section_count: int

class PRDResult(BaseModel):
    success: bool
    filepath_md: str
    filepath_json: str
    feature_count: int
    epic_count: int

class ArtifactResult(BaseModel):
    success: bool
    filepath: str
    label: str
