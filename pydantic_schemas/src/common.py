from pydantic import BaseModel, Field
from typing import Literal, Optional

class System(BaseModel):
    project_id: str = Field(default=None, description="Project ID")
    profile: Optional[str] = Field(default=None, description="Digitizer Profile")
    physical_object_id: Optional[str] = Field(default=None, description="Physical Object ID")
    sequence_id: int = Field(default=None, description="Sequence ID")

