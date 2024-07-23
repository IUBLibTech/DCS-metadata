import logging
import yaml
from pathlib import Path
import sys


def get_profile(pname):
    # Load the profile
    profile = Path(sys.path[0], "../etc/", pname + ".yaml")
    if not profile.exists():
        logging.error(f"Profile {pname} doesn't exist")
        exit(1)
    with open(profile) as f:
        profile = yaml.safe_load(f)
    return profile