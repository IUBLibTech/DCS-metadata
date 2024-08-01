from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional, ClassVar
from enum import Enum

from .. import UNSET
from ..common import SystemBase, MediaBase, PhysicalDetailsBase, ProblemsBase, string_enum, SequenceBase


class OpenReelAudio_Media(MediaBase):
    """Physical Description of OpenReelTape carrier"""
    #class System(SystemBase):
    #    schema_name: Literal["open_reel_audio-media@v1"] = "open_reel_audio-media@v1"
    system: SystemBase = Field(default_factory=SystemBase)
    media_type: Literal["open_reel_audio"] = "open_reel_audio"

    class PhysicalDetails(PhysicalDetailsBase):
        model_config = ConfigDict(use_enum_values=True)
        tape_brand: str = Field(default=UNSET, description="Brand of the tape media")
        reel_size: float = Field(default=7, description="Reel size in inches")
        format_duration: str = Field(default=UNSET, description="Nominal duration of the media")
        tape_base: str = Field(default="n/a", description="Base material for the tape")
        # are there supposed to be choices here?
        track_configuration: str = Field(default="stereo", description="Recorded Track Configuration")
        calculated_directions: int = Field(default=2, description="Calculated number of directions recorded onto the media")
        actual_directions: int = Field(default=2, description="Actual number of directions recorded onto the media")


    physical_details: PhysicalDetails = Field(default_factory=PhysicalDetails)

    class Problems(ProblemsBase):
        pack_deformation: str = Field(default="n/a", description="Details of tape pack deformation")
        preservation_problems: str = Field(default="n/a", description="Details of preservation problems with the media")
        structural_damage: str = Field(default="n/a", description="Details of any structural damage to the media")
    
    problems: Problems = Field(default_factory=Problems)


class OpenReelAudio_Sequence(SequenceBase):
    #class System(SystemBase):
    #    schema_name: Literal["open_reel_audio-sequence@v1"] = "open_reel_audio-sequence@v1"
    system: SystemBase = Field(default_factory=SystemBase)

    model_config = ConfigDict(use_enum_values=True)
    TapeSpeed: ClassVar = string_enum('TapeSpeed', ['7.5 ips', '3.75 ips', '1.875 ips', '0.9375 ips', '0.46875 ips', 'unknown'])
    tape_speed: TapeSpeed = Field(default='unknown', description="tape playback speed")
    signal_chain: str = Field(default='TBD', description="to be determined signal chain")
    SoundField: ClassVar = string_enum('SoundField', ['stereo', 'mono'])
    sound_field: SoundField = Field(default="stereo", description="Recorded sound field")
    reference_fluxivity: str = Field(default='n/a', description="Reference fluxivity")
    gain: str = Field(default='n/a', description="Gain")
    output_voltage: str = Field(default='n/a', description="Output voltage")
    peak_dbfs: str = Field(default='n/a', description="peak dBfs")                             
