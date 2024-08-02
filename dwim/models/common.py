from pydantic import BaseModel, Field
from typing import Literal, Optional
from . import UNSET
from dwim.utils import string_enum

class System(BaseModel):
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
    comments: str = Field(default="no comment",
                          description="Comments noting anything unusual about the condition of the media")


class MediaBase(BaseModel):
    system: System # placeholder for media-specific subclass
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
    system: System # placeholder for media-specific subclass
    label: str = Field(default="n/a", 
                       description="Label to identify the part of the media being digitized")
    comments: str = Field(default="no comment",
                          description="Comments for anything strange or abnormal about the content")
    

SeverityScale = string_enum("SeverityScale", ['none', 'minor', 'moderate', 'severe'])    

CommonTapeProblems = string_enum("CommonTapeProblems", ["damaged tape", "damaged shell",
                                                        "fungus", "soft binder syndrome",
                                                        "other contaminants", "vinegar syndrome"])


class AudioSignalChain(BaseModel):
    data: str = Field(default="TBD", description="Audio Signal chain information TBD")


class VideoSignalChain(BaseModel):
    data: str = Field(default="TBD", description="Video Signal chain information TBD")


VideoStandard = string_enum("VideoStandard", ['ntsc', 'pal', 'secam', 'unknown'])
VideoImageFormat = string_enum("VideoImageFormat", ['4:3', '16:9', '4:3 anamorphic', '4:3 letterbox'])
