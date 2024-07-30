from pathlib import Path
from .profiles import Profile
import logging
import re
import getpass
from datetime import datetime
from .schemas import Schema
import yaml
from .utils import format_string_to_regex, validate_id


class Project:
    def __init__(self, rootdir: Path, name: str, profile: Profile, create: bool=False):
        """Load or create a project"""
        # verify the project id    
        if not re.match(format_string_to_regex(profile.project.id_pattern)[0], name):
            raise ValueError(f"The id {name} doesn't match the required pattern {profile.project.id_pattern}")
            
        self.name = name
        self.profile = profile
        self.project_root = rootdir / name
        if not self.project_root.exists():
            # This project doesn't exist, so instantiate it if we're supposed to
            if not create:
                raise FileNotFoundError("Project doesn't exist")
            
            self.project_root.mkdir()

            # create the project file.
            project_schema = Schema(profile.project.json_schema)
            project = project_schema.create_skeleton()
            project['project_information']['creator'] = getpass.getuser()
            project['project_information']['create_date'] = datetime.strftime(datetime.now(), "%Y-%m-%d")
            with open(self.project_root / "project.yaml", "w") as f:
                f.write(project_schema.get_yaml_text(project))

        # load the project
        with open(self.project_root / "project.yaml") as f:
            self.project = yaml.safe_load(f)

        
    def add_physical_object(self, physical_id: str, physical_type: str):
        """Add a new physical object with the given ID and type"""
        po_path = self.project_root / physical_id
        if (po_path).exists():
            raise FileExistsError(f"Physical object with ID {physical_id} already exists")
        
        # get the configuration and validate the 
        config = self.profile.get_po_config(physical_type)        
        id_fields = validate_id(physical_id, config.id_pattern, config.id_validators, exact=True)
                
        # get the schema for this type
        schema = Schema(f"media/{physical_type}-media")
        media = schema.create_skeleton()
        media = schema.apply_defaults(media, config.media_defaults)
 
        po_path.mkdir()
        with open(po_path / "physical_object.yaml", "w") as f:
            f.write(schema.get_yaml_text(media))
        
        if config.sequence_count:
            # create sequence stubs
            for s in range(1, config.sequence_count + 1):
                self.add_sequence(physical_id, physical_type, s)



    def add_sequence(self, physical_id, physical_type, seqno):
        po_path: Path = self.project_root / physical_id
        if not po_path.exists():
            raise FileNotFoundError(f"Physical object with ID {physical_id} doesn't exist")
        config = self.profile.get_po_config(physical_type)        
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
                seq_meta = schema.apply_defaults(seq_meta, {'sequence': seqno, **config.sequence_defaults})
                with open(mdfile, "w") as f:
                    f.write(schema.get_yaml_text(seq_meta))