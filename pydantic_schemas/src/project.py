from pydantic import BaseModel, Field
from typing import Literal

from common import System

class PSystem(System):
    """System Information"""
    schema: Literal["project@v1"] = "project@v1"


class Contact(BaseModel):
      name: str = Field(description="Contact Name")
      email: str = Field(description="Contact Email")

class ProjectInfo(BaseModel):
    """Project Information"""
    creator: str = Field(default='', description="Project Creator Username")
    creator_name: str = Field(default='', description="Project Creator Name")
    create_date: str = Field(default='', description="Project creation date")
    completion_date: str = Field(default='', description="Completion date")
    contacts: list[Contact] = Field(default_factory=list,
                                    description="List of contacts for this project")
    comments: str = Field(default='no comment', description="Comments about the project")


class OtherIdentifier(BaseModel):
    scope: str = Field(description="Identifier Scope")
    identifier: str = Field(description="Identifier")

class Identifiers(BaseModel):
    iucat_barcode: str = Field(description="IUCAT Barcode"),
    iucat_catkey: str = Field(description="IUCAT Catalog Key"),
    call_number: str = Field(description="Call Number"),
    other_identifiers: list[OtherIdentifier] = Field(description="Other identifiers")


     

class DescriptiveMetadata(BaseModel):
    """Thar be descriptive metadata here"""
    title: str = Field("Project Title")
    identifiers: Identifiers = Field("Project identifiers")

class Project(BaseModel):
    system: PSystem = Field(default_factory=PSystem,
                            description="System Information")
    project_info: ProjectInfo = Field(default_factory=ProjectInfo,
                                      description="Project Information")
    descriptive_metadata: DescriptiveMetadata = Field(default_factory=DescriptiveMetadata)



import yaml
if __name__ == "__main__":
    p = Project()
    print(yaml.safe_dump(p.model_json_schema()))
    print("-----------")
    print(yaml.safe_dump(p.model_dump()))