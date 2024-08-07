from pydantic import BaseModel, Field
from typing import Literal

from . import UNSET
from .common import System

class Structure(BaseModel):
    """Structural Information"""
    system: System = Field(default_factory=System,
                            description="system information")
    object_structure: list[str] = Field(default_factory=list,
                                        description="Order the physical objects appear")
    
