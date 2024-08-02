from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional, ClassVar
from enum import Enum

from .. import UNSET
from ..common import AudioSignalChain, CommonTapeProblems, SeverityScale, System, MediaBase, PhysicalDetailsBase, ProblemsBase, SequenceBase
from dwim.utils import string_enum

class Audiocassette_Media(MediaBase):
    """Physical Description of Audiocassette carrier"""
    system: System = Field(default_factory=System)
    media_type: Literal["audiocassette"] = "audiocassette"

    class PhysicalDetails(PhysicalDetailsBase):
        model_config = ConfigDict(use_enum_values=True)
        media_brand: str = Field(default=UNSET, description="Brand of the tape media")
        nominal_duration: str = Field(default=UNSET, description="Nominal duration of the media")
        
        CassType: ClassVar = string_enum('CassType', ['compact', "micro", "mini"])
        carrier_size: CassType = Field(default="compact", description="Type of cassette")                
        TapeType: ClassVar = string_enum('TapeType', ['unknown', 'I', 'II', 'III', 'IV'])
        tape_type: str = Field(default="I", description="Tape type / formulation")

    physical_details: PhysicalDetails = Field(default_factory=PhysicalDetails)

    class Problems(ProblemsBase):        
        pack_deformation: SeverityScale = Field(default="none", description="Severity of tape pack deformation")
        common_problems: CommonTapeProblems = Field(default_factory=list, description="Common tape problems",
                                                    json_schema_extra={'uniqueItems': True})

    problems: Problems = Field(default_factory=Problems)


class AudioCassette_Sequence(SequenceBase):
    model_config = ConfigDict(use_enum_values=True)
    system: System = Field(default_factory=System)
    signal_chain: AudioSignalChain = Field(default_factory=AudioSignalChain,
                                           description="The signal chain")
    TapeSpeed: ClassVar = string_enum('TapeSpeed', ['3.75 ips', '1.875 ips', '0.9375 ips', '0.46875 ips', 'unknown'])
    playback_speed: TapeSpeed = Field(default='1.875 ips', description="tape playback speed")
    NoiseReduction: ClassVar = string_enum('NoiseReduction', ['none', 'Dolby', 'Dolby B', 'Dolby C'])
    noise_reduction: NoiseReduction = Field(default="none", description="Noise reduction applied during capture")        
    SoundField: ClassVar = string_enum('SoundField', ['stereo', 'mono'])
    sound_field: SoundField = Field(default="stereo", description="Recorded sound field")
                             
