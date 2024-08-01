from pydantic import BaseModel, Field
from typing import Literal

from . import UNSET
from .common import SystemBase

class Project(BaseModel):
    """Digitization Project"""
    #class PSystem(SystemBase):
    #    schema_name: Literal["project@v1"] = "project@v1"
    system: SystemBase = Field(default_factory=SystemBase)

    class ProjectInfo(BaseModel):
        """Project Information"""
        creator: str = Field(default='', description="Project Creator Username")
        creator_name: str = Field(default='', description="Project Creator Name")
        create_date: str = Field(default='', description="Project creation date")
        completion_date: str = Field(default='', description="Completion date")    

        class Contact(BaseModel):
            """Contact Information"""  
            name: str = Field(default=UNSET, description="Contact Name")
            email: str = Field(default=UNSET, description="Contact Email",
                            json_schema_extra={'format': 'email'})    
        contacts: list[Contact] = Field(default_factory=lambda: list([Project.ProjectInfo.Contact()]),
                                        description="List of contacts for this project",
                                        min_length=1)
        comments: str = Field(default='no comment', description="Comments about the project")

    project_information: ProjectInfo = Field(default_factory=ProjectInfo)

    class DescriptiveMetadata(BaseModel):
        """Project Descriptive Metadata"""
        title: str = Field("Project Title")
        class Identifiers(BaseModel):
            "Project Identifiers"
            iucat_barcode: str = Field(default='', description="IUCAT Barcode")
            iucat_catkey: str = Field(default='', description="IUCAT Catalog Key")
            call_number: str = Field(default='', description="Call Number")
            class ScopedIdentifier(BaseModel):
                "An identifier with a scope"
                scope: str = Field(default=UNSET, description="Identifier Scope")
                identifier: str = Field(default=UNSET, description="Identifier")
            other_identifiers: list[ScopedIdentifier] = Field(description="Other identifiers",
                                                              default_factory=list)
        identifiers: Identifiers = Field(description="Project identifiers",
                                         default_factory=Identifiers)

    descriptive_metadata: DescriptiveMetadata = Field(default_factory=DescriptiveMetadata)

