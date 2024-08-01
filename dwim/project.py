from pathlib import Path
import logging
import re
#from .schemas import Schema
from .model import Model
import yaml
from .utils import validate_id
from .profiles import Profile

class Project:
    def __init__(self, rootdir: Path, name: str, create: bool=False, defaults: dict=None):
        """Load or create a project"""
        # verify the project id - I don't care, except that it can only be
        # letters, digits, dashes, and underscores.
        if not re.match("^[A-Za-z0-9][A-Za-z0-9_\\-]{3,}$", name):
            raise ValueError("The project ID must be at least 4 characters, start with a letter or number and must only contain letters, numbers, dashes, and underscores")

        self.name = name
        self.project_root = rootdir / name
        if not self.project_root.exists():
            # This project doesn't exist, so instantiate it if we're supposed to
            if not create:
                raise FileNotFoundError("Project doesn't exist")
            
            # create the project file and directory structure
            self.project_root.mkdir()
            project = Model("project")                        
            if defaults:
                project.patch(defaults)
            project.patch({"system.project_id": name})
            with open(self.project_root / "project.yaml", "w") as f:
                f.write(project.get_yaml_text())

        self.refresh_project()


    def refresh_project(self):        
        """Load the project data from the disk"""
        # load the project
        with open(self.project_root / "project.yaml") as f:
            self.project = yaml.safe_load(f)

        # load the physical objects
        ...




    def add_physical_object(self, profile: Profile, physical_id: str, physical_type: str,
                            defaults: dict=None, seq_defaults: dict=None):
        """Add a new physical object with the given ID and type"""
        po_path = self.project_root / physical_id
        if (po_path).exists():
            raise FileExistsError(f"Physical object with ID {physical_id} already exists")
        
        # get the configuration and validate the 
        config = profile.get_po_config(physical_type)        
        id_fields = validate_id(physical_id, config.id_pattern, config.id_validators, exact=True)
                
        # get the schema for this type
        media = Model(f"media/{physical_type}-media")        
        media.patch(config.media_defaults)
        media.patch(defaults)
        media.patch({'system.profile': profile.name,
                     'system.project_id': self.name,
                     'system.physical_object_id': physical_id})
 
        po_path.mkdir()
        with open(po_path / "physical_object.yaml", "w") as f:
            f.write(media.get_yaml_text())
        
        if config.sequence_count:
            # create sequence stubs
            for s in range(1, config.sequence_count + 1):
                self.add_sequence(profile, physical_id, physical_type, s, seq_defaults)


    def add_sequence(self, profile: Profile, physical_id, physical_type, seqno, defaults: dict=None):
        """Add a media sequence to the physical object"""
        po_path: Path = self.project_root / physical_id
        if not po_path.exists():
            raise FileNotFoundError(f"Physical object with ID {physical_id} doesn't exist")
        config = profile.get_po_config(physical_type)        
        id_fields = validate_id(physical_id, config.id_pattern, config.id_validators, exact=True)

    
        
        for use, usedata in config.uses.items():
            if usedata.optional:
                continue
            
            # create media stub file
            (po_path / usedata.pattern.format(**id_fields, sequence_id=seqno)).touch()
            #  create metadata if it's specified.
            if usedata.has_metadata:
                seq_meta = Model(f"media/{physical_type}-sequence")
                mdfile = po_path / ((usedata.pattern.format(**id_fields, sequence_id=seqno)) + ".yaml")
                if mdfile.exists():
                    logging.warn(f"Not overwriting {mdfile} when creating sequence")
                    continue                
                seq_meta.patch(config.sequence_defaults, variables={'project_id': self.name,
                               'physical_object_id': physical_id,
                               'sequence_id': seqno})
                if defaults:
                    seq_meta.patch(defaults)
                seq_meta.patch({'system.profile': profile.name,
                               'system.project_id': self.name,
                               'system.physical_object_id': physical_id,
                               'system.sequence_id': seqno})
                                
                with open(mdfile, "w") as f:
                    f.write(seq_meta.get_yaml_text())

