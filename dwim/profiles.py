import logging
import yaml
from pathlib import Path
import sys
from pydantic import BaseModel, Field
from typing import Any
from mergedeep import merge


class ProjectConfig(BaseModel):
    """Project Configuration"""
    id_pattern: str = "{id}"
    id_validators: dict[str, list] = Field(default_factory=dict)
    json_schema: str = "project.json"


class PhysicalConfig(BaseModel):
    id_pattern: str = "{id}"
    id_validators: dict[str, list] = Field(default_factory=dict)
    isa: list[str] = Field(default_factory=list)
    media_defaults: dict[str, Any] = Field(default_factory=dict)
    sequence_count: int = 0
    sequence_defaults: dict[str, Any] = Field(default_factory=dict)
    uses: dict[str, "UseConfig"] = Field(default_factory=dict)
    
    
class UseConfig(BaseModel):
    pattern: str
    has_metadata: bool = False
    optional: bool = False


class Profile(BaseModel):
    """Profile-specific functionality, based on a configuration file"""
    name: str
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    physical_objects: dict[str, dict[str, Any]] = Field(default_factory=dict)

    def get_po_config(self, physical_type: str) -> PhysicalConfig:
        """Get the physical object configuration, setting up inheritance as
           needed."""
        if physical_type not in self.physical_objects:
            raise KeyError(f"Physical type {physical_type} not defined!")
        if physical_type == 'default' or physical_type.startswith('_'):
            raise KeyError(f"The physical type specified is a reserved name")
                
        config = {}
        for x in ['default', *self.physical_objects[physical_type].get('isa', []), physical_type]:
            if x not in self.physical_objects:
                raise ValueError(f"The parent physical object type {x} isn't defined!")
            merge(config, self.physical_objects[x])

        return PhysicalConfig(**config)





def load_profile(name: str):
    """Load the default profile and override it with data from the named profile
       if it exists"""
    profiles = []
    for n in ("default", name):    
        pfile = Path(sys.path[0], f"../etc/profile_{n}.yaml")
        if pfile.exists():
            with open(pfile) as f:
                profiles.append(yaml.safe_load(f))
        else:
            profiles.append({})
    profile = merge({}, *profiles)
    return Profile(**profile)

