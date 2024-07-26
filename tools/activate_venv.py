"""
Find and Activate the virtual environment
"""
import __main__
import os
from pathlib import Path
import platform
import sys


def find_venv():
    """Find a .venv directory or return None if one can't be found"""
    here = Path(sys.path[0]) # start in the script directory
    for _ in range(2):
        if (here / ".venv").is_dir():
            return str((here / ".venv").absolute())
        here = here.parent
    return None


venv = find_venv()
if not venv:
    print("ERROR: Cannot locate .venv for this script", file=sys.stderr)
    exit(99)

if os.environ.get("VIRTUAL_ENV", '') != venv:
    # we haven't activated the venv we found, let's do that in the same
    # way that the activate script does.
    os.environ['VIRTUAL_ENV'] = venv
    os.environ['PATH'] = f"{venv}/bin:{os.environ['PATH']}"
    os.environ.pop('PYTHONHOME', None)

    # restart the script using the new environment        
    this_script = str(Path(__main__.__file__).resolve())    
    os.execve(this_script, sys.argv, os.environ)