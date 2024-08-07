from pathlib import Path
import yaml
import sys
import jsonpath_ng 
import logging
import json
from dwim.models.project import Project
from dwim.models.media.audiocassette import Audiocassette_Media, AudioCassette_Sequence
from dwim.models.media.open_reel_audio import OpenReelAudio_Media, OpenReelAudio_Sequence
from dwim.models.media.betacam import Betacam_Media, Betacam_Sequence
from dwim.models.media.umatic import Umatic_Media, Umatic_Sequence
from dwim.models.structure import Structure
from dwim.models import UNSET

model_map = {
    'project': Project,
    'audiocassette-media': Audiocassette_Media,
    'audiocassette-sequence': AudioCassette_Sequence,
    'open_reel_audio-media': OpenReelAudio_Media,
    'open_reel_audio-sequence': OpenReelAudio_Sequence,
    'betacam-media': Betacam_Media,
    'betacam-sequence': Betacam_Sequence,
    'umatic-media': Umatic_Media,
    'umatic-sequence': Umatic_Sequence,
    'structure': Structure,
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
        #print("Before patch:", data)
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
        #print("After patch:", data)
        self.data = self.model(**data)


    def validate(self):
        """Validate data against this schema"""
        self.model(self.data)


    def get_yaml_text(self, schema: Path=None, clean=True):
        """Get the yaml file text for the data given."""
        # prepend the schema information for the yaml language server        
        txt = f"# yaml-language-server: $schema={schema}\n" if schema else ""
        txt += yaml.safe_dump(self.data.model_dump(), sort_keys=False, default_flow_style=False, 
                              indent=4, width=80)
        if clean:
            # clean up the text itself and clear out "unset" things...
            txt = txt.replace(UNSET, '')
        return txt


    def write_json_schema(self, outfile: Path, rewrite=False):
        """Generate a json schema and write it to the disk"""
        if outfile.is_dir():
            # generate the filename based on the schema name.
            outfile = outfile / f"{self.name}.json"        
        if rewrite or not outfile.exists():
            with open(outfile, "w") as f:
                json.dump(self.model.model_json_schema(), f, indent=4, sort_keys=False)


    def write_file(self, filename: Path, schemadir: Path=None, clean=True):
        """Write out the file"""
        schema = None
        if schemadir:
            schema = schemadir.relative_to(filename.parent, walk_up=True) / f"{self.name}.json"
            self.write_json_schema(schemadir, rewrite=False)
        text = self.get_yaml_text(schema, clean)
        with open(filename, "w") as f:
            f.write(text)


    @staticmethod
    def read_file(filename: Path, empty_ok: bool=False, model_name: str=None) -> "Model":
        """Read a yaml file and return a model for it"""
        if not filename.exists():        
            if empty_ok:
                return Model(model_name)
            raise FileNotFoundError(f"File {filename} doesn't exist")
        
        with open(filename) as f:
            raw_data = yaml.safe_load(f)

        if 'system' in raw_data:
            model_name = raw_data['system'].get("schema_name", None)
            if model_name and model_name in model_map:
                return Model(model_name, raw_data)
        
        raise NotImplementedError("The data file doesn't seem to be valid model")

