from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional, ClassVar
from enum import Enum
import datetime

from .. import UNSET
from ..common import AudioSignalChain, CommonTapeProblems, SeverityScale, System, MediaBase, PhysicalDetailsBase, ProblemsBase, SequenceBase, VideoImageFormat, VideoSignalChain, VideoStandard
from dwim.utils import string_enum

class Umatic_Media(MediaBase):
    """Physical description of Umatic carrier"""
    system: System = Field(default_factory=System)
    media_type: Literal["umatic"] = "umatic"

    class PhysicalDetails(PhysicalDetailsBase):
        model_config = ConfigDict(use_enum_values=True)
        media_brand: str = Field(default=UNSET, description="Brand of the tape media")
        nominal_duration: str = Field(default=UNSET, description="Nominal duration of the media")
        CarrierSize: ClassVar = string_enum("CarrierSize", ["large", "small"])
        carrier_size: CarrierSize = Field(default="small", description="Tape cassette size")
        FormatVersion: ClassVar = string_enum('FormatVersion', ['high band', 'low band', "sp"])
        format_version: FormatVersion = Field(default='high band', description="Recording format")


    physical_details: PhysicalDetails = Field(default_factory=PhysicalDetails)
    
    class Problems(ProblemsBase):              
        common_problems: set[CommonTapeProblems] = Field(default_factory=set, description="Common tape problems")
                                                          #json_schema_extra={'uniqueItems': True})
        cleaned_date: Literal['none'] | datetime.date = Field(default="none", 
                                  description="Cleaning date in YYYY-MM-DD or 'none'")
        baked_date: Literal['none'] | datetime.date = Field(default="none", 
                                  title="Baking date in YYYY-MM-DD or 'none'")
    problems: Problems = Field(default_factory=Problems)


class Umatic_Sequence(SequenceBase):
    model_config = ConfigDict(use_enum_values=True)
    system: System = Field(default_factory=System)
    signal_chain: VideoSignalChain = Field(default_factory=VideoSignalChain,
                                           description="The signal chain")
    SoundField: ClassVar = string_enum('SoundField', ['ch1', 'ch2', 'stereo'])
    sound_field: set[SoundField] = Field(default_factory=lambda: set(["ch1"]), 
                                          description="Recorded sound field",
                                          json_schema_extra={'uniqueItems': True})    
    video_standard: VideoStandard = Field(default="ntsc", description="Video signal standard")
    image_format: VideoImageFormat = Field(default="4:3", description="Video image format")
    