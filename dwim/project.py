from pathlib import Path
import logging
import re
from .schemas import Schema
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
            project_schema = Schema("project")
            project = project_schema.create_skeleton()
            project = project_schema.apply_defaults(project, {"identification.project_id": name})
            if defaults:
                project = project_schema.apply_defaults(project, defaults)
            
            with open(self.project_root / "project.yaml", "w") as f:
                f.write(project_schema.get_yaml_text(project))

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
        schema = Schema(f"media/{physical_type}-media")
        media = schema.create_skeleton()
        media = schema.apply_defaults(media, config.media_defaults)
        media = schema.apply_defaults(media, defaults)
        media = schema.apply_defaults(media, {'profile': profile.name,
                                              'identification.project_id': self.name,
                                              'identification.physical_object_id': physical_id})
 
        po_path.mkdir()
        with open(po_path / "physical_object.yaml", "w") as f:
            f.write(schema.get_yaml_text(media))
        
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

        # create sequence data stubs
        schema = Schema(f"media/{physical_type}-sequence")
        
        for use, usedata in config.uses.items():
            if usedata.optional:
                continue
            
            # create media stub file
            (po_path / usedata.pattern.format(**id_fields, sequence=seqno)).touch()
            #  create metadata if it's specified.
            if usedata.has_metadata:
                mdfile = po_path / ((usedata.pattern.format(**id_fields, sequence=seqno)) + ".yaml")
                if mdfile.exists():
                    logging.warn(f"Not overwriting {mdfile} when creating sequence")
                    continue
                seq_meta = schema.create_skeleton()
                seq_meta = schema.apply_defaults(seq_meta, config.sequence_defaults)
                seq_meta = schema.apply_defaults(seq_meta, {'identification.project_id': self.name,
                                                            'identification.physical_object_id': physical_id,
                                                            'identification.sequence_id': seqno})
                if defaults:
                    seq_meta = schema.apply_defaults(seq_meta, defaults)
                with open(mdfile, "w") as f:
                    f.write(schema.get_yaml_text(seq_meta))

