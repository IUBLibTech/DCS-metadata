from pathlib import Path
import yaml
import sys
import jsonpath_ng 
import logging

from dwim.models.project import Project
from dwim.models.media.audiocassette import Audiocassette_Media, AudioCassette_Sequence
from dwim.models.media.open_reel_audio import OpenReelAudio_Media, OpenReelAudio_Sequence

from dwim.models import UNSET

schema_dir: Path = Path(sys.path[0], "../schemas")

model_map = {
    'project': Project,
    'media/audiocassette-media': Audiocassette_Media,
    'media/audiocassette-sequence': AudioCassette_Sequence,
    'media/open_reel_audio-media': OpenReelAudio_Media,
    'media/open_reel_audio-sequence': OpenReelAudio_Sequence
}


class Model:
    """Data Models"""
    def __init__(self, name, init_data: dict = None):
        if name not in model_map:
            raise KeyError(f"Model {name} is unknown")
        self.name = name
        self.model = model_map[name]        
        self.initialize(init_data)
        

    def initialize(self, data=None):
        """Create an empty model that uses the defaults"""
        if data is None:
            self.data = self.model()
        else:
            self.data = self.model(**data)
        self.patch({'system.schema_name': self.name})


    def patch(self, defaults: dict, create: bool=True, variables: dict = None) -> dict:
        """Apply patches to the data"""                
        data = self.data.model_dump()
        for k, v in defaults.items():
            if variables:
                # try to do variable substitution in the value
                v = str(v).format_map(variables)    
            jpath = jsonpath_ng.parse(k)            
            if create:
                jpath.update_or_create(data, v)        
            else:
                if not jpath.find(data):
                    raise KeyError(f"Setting default value for {k} but it wasn't found in the tree")                    
                jpath.update(data, v)
        self.data = self.model(**data)


    def validate(self):
        """Validate data against this schema"""
        self.model(self.data)


    def get_yaml_text(self, base=None):
        """Get the yaml file text for the data given."""
        # prepend the schema information for the yaml language server        
        if base is None:
            # use the default filesystem path...
            p = (schema_dir / (self.name + ".json")).resolve()
            txt = f"# yaml-language-server: $schema={p}\n"
        else:
            txt = f"# yaml-language-server: $schema={base}{self.name}.json\n"
        
        txt += yaml.safe_dump(self.data.model_dump(), sort_keys=False, default_flow_style=False, 
                              indent=4, width=80)

        # clean up the text itself and clear out "unset" things...
        txt = txt.replace(UNSET, '')

        return txt
