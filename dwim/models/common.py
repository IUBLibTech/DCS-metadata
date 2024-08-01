from pydantic import BaseModel, Field
from typing import Literal, Optional
from enum import Enum
import string

from . import UNSET

def string_enum(classname: str, names: list) -> Enum:
    """Create an enum class where the names map to themselves"""
    def str2identifier(text):
        if text[0] not in string.ascii_letters:
            text = "_" + text
        ntext = ""
        for i, c in enumerate(text):
            if c not in string.ascii_letters or c not in string.digits:
                ntext +=  '_'
            else:
                ntext += c
        return ntext

    return Enum(classname, {str2identifier(x): x for x in names})





class SystemBase(BaseModel):
    """System information"""
    project_id: str = Field(default='', description="Project ID")
    profile: str = Field(default='', description="Digitizer Profile")
    physical_object_id: str = Field(default='', description="Physical Object ID")
    sequence_id: int = Field(default=0, description="Sequence ID")
    schema_name: str = Field(default=UNSET, description="Schema name used")

class PhysicalDetailsBase(BaseModel):
    "Physical Details about the media"
    comments: str = Field(default="no comment",
                          description="Comments noting anything unusual about the media")

class ProblemsBase(BaseModel):
    "Problems with the media"
    ...

class MediaBase(BaseModel):
    system: SystemBase # placeholder for media-specific subclass
    media_type: str # placeholder for media type
    title: str = Field(default="SAME", 
                       description="Title of the physical media if it differs from the project")
    barcode: str = Field(default="no barcode",
                         description="Barcode (or other identifier) for this media")
    digitizer: str = Field(default=UNSET,
                           description="Username of digitization operator")
    digitization_date: str = Field(default=UNSET,
                                   description="Date that the media was digitized",
                                   json_schema_extra={'format': 'date'})
    physical_details: PhysicalDetailsBase # placeholder
    problems: ProblemsBase


class SequenceBase(BaseModel):
    """Information related to a digitization sequence"""
    system: SystemBase # placeholder for media-specific subclass
    label: str = Field(default="n/a", 
                       description="Label to identify the part of the media being digitized")
    comments: str = Field(default="no comment",
                          description="Comments for anything strange or abnormal about the content")
    