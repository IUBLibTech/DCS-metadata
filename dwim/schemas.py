from pathlib import Path
import yaml
import sys
from jsonschema.exceptions import ValidationError
from jsonschema.validators import Draft202012Validator
import jsonpath_ng 
import logging

schema_dir: Path = Path(sys.path[0], "../schemas")

class Schema:
    "JSON Schema Management Stuff"
    def __init__(self, name: str):
        """Load a JSON Schema"""
        self.schema_path = schema_dir / f"{name}.json"
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema {name} doesn't exist")
        self.name = name
        with open(self.schema_path) as f:
            self.schema = yaml.safe_load(f)


    def create_skeleton(self):
        """Create a data structure that uses the schema defaults"""
        return self._create_skeleton(self.schema)
    

    def _create_skeleton(self, schema):
        if 'const' in schema:
            return schema['const']
        match schema.get('type', 'object'):
            case 'object':
                d = {}
                for k in schema.get('required', []):
                    if k in schema['properties']:
                        d[k] = self._create_skeleton(schema['properties'][k])
                    else:
                        d[k] = '__UNSET__'
            case 'array':
                d = []
                for _ in range(schema.get('minContains', 1)):
                    d.append(self._create_skeleton(schema['items']))
            case 'integer' | 'float' | 'string' | 'boolean':
                return schema.get('default', '__UNSET__')
            case _:
                # this is a type we can't handle.  Just return None?
                return None
        return d


    def apply_defaults(self, data: dict, defaults: dict, create=True, validate=False) -> dict:
        """Apply defaults to the data and then validate the result."""        
        errs = []
        for k, v in defaults.items():            
            jpath = jsonpath_ng.parse(k)            
            if create:
                jpath.update_or_create(data, v)        
            else:
                if not jpath.find(data):
                    errs.append(f"Setting default value for {k} but it wasn't found in the tree")
                    continue                    
                jpath.update(data, v)
        
        if validate:
            errs.extend(self.validate(data))
            if errs:
                raise ValueError(f"Data doesn't validate after applying these defaults: {defaults}: \n  *" + "\n  *".join(errs))

        return data


    def validate(self, data):
        """Validate data against this schema"""
        vtor = Draft202012Validator(self.schema)
        errors = []
        error: ValidationError = None
        for error in vtor.iter_errors(data):
            errors.append(str(error))
        return errors
        

    def get_yaml_text(self, data, base=None):
        """Get the yaml file text for the data given."""
        # prepend the schema information for the yaml language server        
        if base is None:                    
            txt = f"# yaml-language-server: $schema={self.schema_path.resolve()}\n"
        else:
            txt = f"# yaml-language-server: $schema={base}{self.name}\n"
        
        txt += yaml.safe_dump(data, sort_keys=False, default_flow_style=False, 
                              indent=4, width=80)

        # clean up the text itself and clear out "unset" things...
        txt = txt.replace('__UNSET__', '')
        txt = txt.replace('[]', '')
        txt = txt.replace('{}', '')
        # special value handlers
        for x in ('null', 'true', 'false'):
            txt = txt.replace(f"'{x}'", x)
        
        return txt
