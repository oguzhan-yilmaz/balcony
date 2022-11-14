import logging
from rich.logging import RichHandler
from rich.console import Console
import os
from pathlib import Path
from yaml import load, dump, Loader, Dumper

HOME_DIR = os.path.expanduser('~')
BALCONY_CONFIG_DIR = os.getenv('BALCONY_CONFIG_DIR', os.path.join(HOME_DIR, '.balcony'))
BALCONY_RELATIONS_DIR = os.getenv('BALCONY_RELATIONS_DIR', os.path.join(BALCONY_CONFIG_DIR, 'relations'))
BALCONY_CONFIG_FILENAME = os.getenv('BALCONY_CONFIG_FILENAME', 'balcony-conf.yaml')
# create the relations directory if not exists
Path(BALCONY_RELATIONS_DIR).mkdir(parents=True, exist_ok=True)

LOG_LEVEL = 'INFO'


_console = Console(color_system="auto", markup=True)
_balcony_loggers = []

def get_rich_console() -> Console:
    """Returns the global defined `rich.console.Console` object for common use. 

    Returns:
        rich.console.Console: rich console object
    """
    return _console



def read_config_file():
    config_filepath = os.path.join(BALCONY_CONFIG_DIR, BALCONY_CONFIG_FILENAME)
    with open(config_filepath,'r') as conf_file:
        data = load(conf_file, Loader=Loader)
    return data

def write_config_file(config_dict):
    config_filepath = os.path.join(BALCONY_CONFIG_DIR, BALCONY_CONFIG_FILENAME)
    with open(config_filepath,'w') as conf_file:
        output = dump(config_dict, conf_file, Dumper=Dumper, default_flow_style=False)     
    return output

def get_installed_apps():
    return read_config_file().get('installed_apps', [])
    
def add_installed_app_to_config(installed_app_name):
    config = read_config_file()
    _console.print(f"{config=}")
    installed_apps = config.get('installed_apps', [])
    _console.print(f"{installed_apps=}")
    
    if installed_app_name and installed_app_name not in installed_apps:
        installed_apps.append(installed_app_name)
    config['installed_apps'] = installed_apps
    _console.print(f"{config}")

    write_config_file(config)


def supress_other_module_logs() -> None:
    """Sets Python modules log levels to `logging.CRITICAL` to supress them."""
    _supress_module_names = ('boto', 'urllib3', 's3transfer', 'boto3', 'botocore', 'nose')
    for _logger_name in logging.Logger.manager.loggerDict.keys():
        if _logger_name in _supress_module_names:
            logging.getLogger(_logger_name).setLevel(logging.CRITICAL)
            

def set_log_level_at_runtime(log_level):
    for _logger in _balcony_loggers:
        _logger.setLevel(log_level)
        # for handler in _logger.handlers:
        #     if isinstance(handler, type(logging.StreamHandler())):
        #         handler.setLevel(log_level)
        #         _logger.debug('Debug logging enabled')

def get_logger(name: str) -> logging.Logger:
    """Logger creation with RichHandler. 

    Args:
        name (str): Logger name. Usually given `__name__`.

    Returns:
        logging.Logger: Logger obj
    """
    supress_other_module_logs()
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=True, console=_console)]
    )
    # logging.FileHandler("debug.log", mode='w')
    
    _logger = logging.getLogger(name)
    _balcony_loggers.append(_logger)
    return _logger
