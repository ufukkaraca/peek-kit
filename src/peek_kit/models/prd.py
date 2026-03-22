from typing import List, Optional
from pydantic import BaseModel

class AcceptanceCriterion(BaseModel):
    description: str

class UserStory(BaseModel):
    persona: str
    action: str
    outcome: str
    acceptance_criteria: List[AcceptanceCriterion]
    technical_notes: Optional[str] = None

class Epic(BaseModel):
    name: str
    description: str
    stories: List[UserStory]

class Persona(BaseModel):
    name: str
    role: str
    job_to_be_done: str
    pain_points: List[str]
    key_features: List[str]

class ValueProposition(BaseModel):
    bet: str
    ui_evidence: str
    replication_effort: str

class InfoGroup(BaseModel):
    name: str
    items: List[str]

class ScreenDefinition(BaseModel):
    name: str
    user_intent: str
    key_elements: List[str]
    primary_action: str
    secondary_actions: List[str]

class EntityAttribute(BaseModel):
    name: str
    type: str

class DataEntity(BaseModel):
    name: str
    attributes: List[EntityAttribute]

class PRDDocument(BaseModel):
    app_name: str
    audit_filename: str
    timestamp: str
    product_overview: str
    target_personas: List[Persona]
    core_value_proposition: List[ValueProposition]
    epics: List[Epic]
    information_architecture: List[InfoGroup]
    key_screens: List[ScreenDefinition]
    data_model: List[DataEntity]
    what_to_replicate: List[str]
    what_to_improve: List[str]
    out_of_scope: List[str]
    open_questions: List[str]
