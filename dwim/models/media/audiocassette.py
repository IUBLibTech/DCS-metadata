from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional, ClassVar
from enum import Enum

from .. import UNSET
from ..common import SystemBase, MediaBase, PhysicalDetailsBase, ProblemsBase, string_enum, SequenceBase


class Audiocassette_Media(MediaBase):
    """Physical Description of Audiocassette carrier"""
    #class System(SystemBase):
    #    schema_name: Literal["audiocassette-media@v1"] = "audiocassette-media@v1"
    system: SystemBase = Field(default_factory=SystemBase)
    media_type: Literal["audiocassette"] = "audiocassette"

    class PhysicalDetails(PhysicalDetailsBase):
        model_config = ConfigDict(use_enum_values=True)
        tape_brand: str = Field(default=UNSET, description="Brand of the tape media")
        format_duration: str = Field(default=UNSET, description="Nominal duration of the media")
        
        CassType: ClassVar = string_enum('CassType', ['compact', "micro", "mini"])
        cassette_type: CassType = Field(default="compact", description="Type of cassette")                
        TapeType: ClassVar = string_enum('TapeType', ['unknown', 'I', 'II', 'III', 'IV'])
        tape_type: str = Field(default="unknown", description="Tape type / formulation")

    physical_details: PhysicalDetails = Field(default_factory=PhysicalDetails)

    class Problems(ProblemsBase):
        pack_deformation: str = Field(default="n/a", description="Details of tape pack deformation")
        preservation_problems: str = Field(default="n/a", description="Details of preservation problems with the media")
        structural_damage: str = Field(default="n/a", description="Details of any structural damage to the media")
    
    problems: Problems = Field(default_factory=Problems)


class AudioCassette_Sequence(SequenceBase):
    #class System(SystemBase):
    #    schema_name: Literal["audiocassette-sequence@v1"] = "audiocassette-sequence@v1"
    system: SystemBase = Field(default_factory=SystemBase)

    model_config = ConfigDict(use_enum_values=True)
    TapeSpeed: ClassVar = string_enum('TapeSpeed', ['3.75 ips', '1.875 ips', '0.9375 ips', '0.46875 ips', 'unknown'])
    tape_speed: TapeSpeed = Field(default='unknown', description="tape playback speed")
    signal_chain: str = Field(default='TBD', description="to be determined signal chain")
    SoundField: ClassVar = string_enum('SoundField', ['stereo', 'mono'])
    sound_field: SoundField = Field(default="stereo", description="Recorded sound field")
    NoiseReduction: ClassVar = string_enum('NoiseReduction', ['none', 'Dolby', 'Dolby B', 'Dolby C'])
    noise_reduction: NoiseReduction = Field(default="none", description="Noise reduction used")
                             
