import os
from pathlib import Path

HOME_DIR = os.path.expanduser('~')
BALCONY_CONFIG_DIR = os.getenv('BALCONY_CONFIG_DIR', os.path.join(HOME_DIR, '.balcony'))
BALCONY_RELATIONS_DIR = os.getenv('BALCONY_RELATIONS_DIR', os.path.join(BALCONY_CONFIG_DIR, 'relations'))

# create the relations directory if not exists
Path(BALCONY_RELATIONS_DIR).mkdir(parents=True, exist_ok=True)


LOG_LEVEL = 'INFO'

INSTALLED_BALCONY_APPS = (
    'balconyapp',
)