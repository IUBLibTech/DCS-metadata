from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional, ClassVar
from enum import Enum

from .. import UNSET
from ..common import AudioSignalChain, CommonTapeProblems, SeverityScale, System, MediaBase, PhysicalDetailsBase, ProblemsBase, SequenceBase, VideoImageFormat, VideoSignalChain, VideoStandard
from dwim.utils import string_enum

class Betacam_Media(MediaBase):
    """Physical Description of OpenReelTape carrier"""
    system: System = Field(default_factory=System)
    media_type: Literal["betacam"] = "betacam"

    class PhysicalDetails(PhysicalDetailsBase):
        model_config = ConfigDict(use_enum_values=True)
        media_brand: str = Field(default=UNSET, description="Brand of the tape media")
        nominal_duration: str = Field(default=UNSET, description="Nominal duration of the media")
        CarrierSize: ClassVar = string_enum("CarrierSize", ["large", "small"])
        carrier_size: CarrierSize = Field(default="small", description="Tape cassette size")
        BetacamType: ClassVar = string_enum("BetacamType", ["oxide", "sp", "digital", "sx", "imx"])
        tape_type: BetacamType = Field(default="sp", 
                                       description="Betacam tape type")
        
    physical_details: PhysicalDetails = Field(default_factory=PhysicalDetails)
    
    class Problems(ProblemsBase):                
        common_problems: CommonTapeProblems = Field(default_factory=list, description="Common tape problems",
                                                    json_schema_extra={'uniqueItems': True})
        cleaned_date: str = Field(default="none", 
                                  description="Cleaning date",
                                  json_schema_extra={'format': 'date'})
        baked_date: str = Field(default="none", 
                                  description="Baking date",
                                  json_schema_extra={'format': 'date'})

    problems: Problems = Field(default_factory=Problems)


class Betacam_Sequence(SequenceBase):
    model_config = ConfigDict(use_enum_values=True)
    system: System = Field(default_factory=System)
    signal_chain: VideoSignalChain = Field(default_factory=VideoSignalChain,
                                           description="The signal chain")
    SoundField: ClassVar = string_enum('SoundField', ['stereo', 'mono', 'split tracks', 'ch1', 'ch2', 'ch3', 'ch4'])
    sound_field: list[SoundField] = Field(default_factory=lambda: list(["stereo"]), 
                                          description="Recorded sound field",
                                          json_schema_extra={'uniqueItems': True})    
    video_standard: VideoStandard = Field(default="ntsc", description="Video signal standard")
    image_format: VideoImageFormat = Field(default="4:3", description="Video image format")
    
