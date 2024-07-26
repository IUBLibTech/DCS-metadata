from pathlib import Path
import yaml
import sys

schema_dir = Path(sys.path[0], "../schemas")


def prep_yaml_file(data, schema_path: Path):
    # generate the basic dump...
    txt = yaml.safe_dump(data, sort_keys=False, default_flow_style=False, 
                         indent=4, width=80)
    # prepend the schema information for the yaml language server
    txt = f"# yaml-language-server: $schema={schema_path.resolve()}\n{txt}"

    # clean up the text itself and clear out "unset" things...
    txt = txt.replace('__UNSET__', '')
    txt = txt.replace('[]', '')
    txt = txt.replace('{}', '')
    txt = txt.replace("'null'", 'null')

    return txt


def populate_schema_defaults(schema_file: Path):
    with open(schema_file) as f:
        schema = yaml.safe_load(f)
    default = create_defaults_from_schema(schema)
    return default


def create_defaults_from_schema(schema):
    if 'const' in schema:
        return schema['const']
    match schema.get('type', 'object'):
        case 'object':
            d = {}
            for k in schema.get('required', []):
                if k in schema['properties']:
                    d[k] = create_defaults_from_schema(schema['properties'][k])
                else:
                    d[k] = '__UNSET__'
        case 'array':
            d = []
            for _ in range(schema.get('minContains', 1)):
                d.append(create_defaults_from_schema(schema['items']))
        case 'integer' | 'float' | 'string' | 'boolean':
            return schema.get('default', '__UNSET__')
        case _:
            # this is a type we can't handle.  Just return None?
            return None
    return d

