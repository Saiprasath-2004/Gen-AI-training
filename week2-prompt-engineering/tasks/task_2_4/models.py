from pydantic import BaseModel, Field
from typing import Optional

class Incident(BaseModel):
    severity: Optional[str]
    service: Optional[str]
    duration_minutes: Optional[int]
    customer_impact: Optional[str]
    root_cause: Optional[str]
    recommended_actions: Optional[str] = Field(alias="recommended_action")