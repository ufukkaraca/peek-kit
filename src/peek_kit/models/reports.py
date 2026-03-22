from typing import List, Optional
from pydantic import BaseModel

class Scorecard(BaseModel):
    learnability: int
    efficiency: int
    error_prevention: int
    feedback: int
    consistency: int
    accessibility: int
    visual_hierarchy: int
    error_recovery: int
    overall_score: float
    rationale: str

class Feature(BaseModel):
    name: str
    description: str
    access_path: str
    availability: str

class FeatureCategory(BaseModel):
    category_name: str
    features: List[Feature]

class FeatureMap(BaseModel):
    categories: List[FeatureCategory]

class Finding(BaseModel):
    severity: str
    title: str
    screens: List[str]
    artifact_reference: Optional[str] = None
    description: str
    recommendation: str
    effort: str

class SecretSauceItem(BaseModel):
    name: str
    description: str
    why_users_love_it: str
    replication_effort: str
    artifact_reference: Optional[str] = None

class PositiveItem(BaseModel):
    title: str
    explanation: str
    why_good: str
    artifact_reference: Optional[str] = None

class Coverage(BaseModel):
    screens_visited: List[str]
    screens_not_reached: List[str]
    auth_tier: str

class AccessibilityAssessment(BaseModel):
    keyboard_navigation: str
    label_quality: str
    contrast_issues: str
    api_gaps: str
    overall_impression: str

class AuditReport(BaseModel):
    app_name: str
    analysis_date: str
    analyst: str
    coverage_level: str
    limitations: Optional[str] = None
    executive_summary: str
    scorecard: Scorecard
    feature_inventory: FeatureMap
    flow_map: str
    what_they_do_well: List[PositiveItem]
    what_needs_work: List[Finding]
    secret_sauce: List[SecretSauceItem]
    design_philosophy: str
    monetization_patterns: str
    accessibility: AccessibilityAssessment
    exploration_coverage: Coverage
