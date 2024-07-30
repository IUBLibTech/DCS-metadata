import logging
import yaml
from pathlib import Path
import sys
from pydantic import BaseModel, Field


class Config(BaseModel):
    """Configuration for DWIM Tools"""
    schema_base: str
    project_root: str


def load_config():
    """Load the configuration"""
    with open(Path(sys.path[0], "../etc/dwim.yaml")) as f:
        return Config(**yaml.safe_load(f))
