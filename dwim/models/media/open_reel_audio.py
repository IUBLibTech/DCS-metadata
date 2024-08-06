from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional, ClassVar
from enum import Enum

from .. import UNSET
from ..common import AudioSignalChain, CommonTapeProblems, SeverityScale, System, MediaBase, PhysicalDetailsBase, ProblemsBase, SequenceBase
from dwim.utils import string_enum

class OpenReelAudio_Media(MediaBase):
    """Physical Description of OpenReelTape carrier"""
    system: System = Field(default_factory=System)
    media_type: Literal["open_reel_audio"] = "open_reel_audio"

    class PhysicalDetails(PhysicalDetailsBase):
        model_config = ConfigDict(use_enum_values=True)
        media_brand: str = Field(default=UNSET, description="Brand of the tape media")
        nominal_duration: str = Field(default=UNSET, description="Nominal duration of the media")
        carrier_size: float = Field(default=7, description="Reel size in inches")
        tape_thickness: float = Field(default=1.4, description="Tape thickness in mil")        
        tape_base: str = Field(default="n/a", description="Base material for the tape")
        TapeConfiguration: ClassVar = string_enum("TapeConfiguration", ['full', 'half', 'quarter', 'unknown'])
        track_configuration: TapeConfiguration | list[TapeConfiguration]= Field(default="half", 
                                                                                description="Recorded Track Configuration",
                                                                                json_schema_extra={'uniqueItems': True})
        calculated_directions: int = Field(default=2, description="Calculated number of directions recorded onto the media")
        recorded_directions: int = Field(default=2, description="Actual number of directions recorded onto the media")

    physical_details: PhysicalDetails = Field(default_factory=PhysicalDetails)
    
    class Problems(ProblemsBase):   
        model_config = ConfigDict(use_enum_values=True)     
        pack_deformation: SeverityScale = Field(default="none", description="Severity of tape pack deformation")
        common_problems: list[CommonTapeProblems] = Field(default_factory=list, description="Common tape problems",
                                                    json_schema_extra={'uniqueItems': True})

    problems: Problems = Field(default_factory=Problems)


class OpenReelAudio_Sequence(SequenceBase):
    model_config = ConfigDict(use_enum_values=True)
    system: System = Field(default_factory=System)
    signal_chain: AudioSignalChain = Field(default_factory=AudioSignalChain,
                                           description="The signal chain")
    TapeSpeed: ClassVar = string_enum('TapeSpeed', ['30 ips', '15 ips', '7.5 ips', '3.75 ips', '1.875 ips', '0.9375 ips', '0.46875 ips', 'unknown'])
    tape_speed: TapeSpeed | list[TapeSpeed] = Field(default='7.5 ips', description="tape playback speed")
    SoundField: ClassVar = string_enum('SoundField', ['stereo', 'mono', 'dual mono'])
    sound_field: SoundField = Field(default="stereo", description="Recorded sound field")

