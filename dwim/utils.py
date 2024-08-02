"""
Useful utilities
"""
from string import Formatter
import re
import luhn
from enum import Enum
import string


def format_string_to_regex(fmtstring, strmatch='*'):
    """Given a python format string, convert it to a regex and return field names"""
    regex = ""
    groups = {}
    for text, variable, format, conversion in Formatter().parse(fmtstring):
        regex += _escape_regex_text(text)
        if variable:
            vtype = 's'
            regex += f"(?P<{variable}>"
            if not format:
                regex += f".{strmatch}?"
            else:
                # split up the format string into parts...
                ftype = format[-1]
                fwidth = format[0:-1] if len(format) > 1 else None
                fprecision = None
                if fwidth and '.' in fwidth:
                    fwidth, fprecision = fwidth.split('.')
                vtype = vtype
                match ftype:
                    case 's':
                        if fwidth:
                            regex += f".{{{fwidth}}}"
                        else:
                            regex += f".{strmatch}?"
                    case 'd':
                        if fwidth:
                            regex += f"\\d{{{int(fwidth)}}}"
                        else:
                            regex += "\\d+"
                        pass
                    case 'f':
                        regex += "\\d+\\.\\d+"
                    case _:
                        raise ValueError(f"Don't know how to parse format: {format}")                
            regex += ")"
            groups[variable] = vtype

    return regex, groups


def _escape_regex_text(text):
    for c in ('.', '{', '}', '[', ']', '?', '*'):
        text = text.replace(c, f'\\{c}')
    return text


def validate_id(the_id: str, id_pattern: str, id_validators: dict, exact=False) -> dict[str, str]:
    """Validate an ID pattern using the validators and return the parts and their values"""
    id_pat, vdata = format_string_to_regex(id_pattern)
    if m := re.match("^" + id_pat + ('$' if exact else ''), the_id):
        parts = m.groupdict()
        errors = []
        if id_validators:
            for field, validator in id_validators.items():
                if field in parts:
                    vname, *vargs = validator
                    match vname:
                        case 'luhn':
                            # validate a barcode
                            if not luhn.verify(parts[field]):
                                errors.append(f"Validation of {field} failed:  Luhn check digit is wrong for '{parts[field]}'")
                        case 'regex':
                            # look for a specific regex
                            if not re.match(vargs[0], parts[field]):
                                errors.append(f"Validation of {field} failed:  regex '{vargs[0]}' doesn't match '{parts[field]}'")
                        case _:
                            raise ValueError(f"Unknown id validator {vname} for field {field}")
        if errors:
            raise ValueError(f"The id '{the_id}' failed for these reason: \n   *" + "\n    *".join(errors))
        
        # convert values as needed for round-trippery
        dmap = {'s': str, 'd': int, 'f': 'float'}
        for k, v in vdata.items():
            if k in parts and v in dmap:
                parts[k] = dmap[v](parts[k])

        return parts
    else:
        raise ValueError(f"ID Match for '{the_id}' fails for pattern '{id_pattern}'")
    

def string_enum(classname: str, names: list) -> Enum:
    """Create an enum class where the names map to themselves"""
    def str2identifier(text):
        if text[0] not in string.ascii_letters:
            text = "_" + text
        ntext = ""
        for i, c in enumerate(text):
            if c not in string.ascii_letters or c not in string.digits:
                ntext +=  '_'
            else:
                ntext += c
        return ntext

    return Enum(classname, {str2identifier(x): x for x in names})


if __name__ == "__main__":    
    regex, fields = format_string_to_regex("MDPI_{barcode:14d}_{sequence:02d}_{use:s}.mp4", strmatch='*')
    print(regex, fields)
    m = re.match(regex, "MDPI_40000001229337_01_high_20160204_083240.mp4")
    print(m, m.groupdict())

