import logging
from rich.logging import RichHandler
from rich.console import Console
import os
from pathlib import Path

HOME_DIR = os.path.expanduser('~')

# Defaults to ~/.balcony/
BALCONY_CONFIG_DIR = os.getenv('BALCONY_CONFIG_DIR', os.path.join(HOME_DIR, '.balcony'))

# Defaults to ~/.balcony/relations/
BALCONY_RELATIONS_DIR = os.getenv('BALCONY_RELATIONS_DIR', os.path.join(BALCONY_CONFIG_DIR, 'relations'))

# create the relations directory if not exists
Path(BALCONY_RELATIONS_DIR).mkdir(parents=True, exist_ok=True)

LOG_LEVEL = 'INFO'

_console = Console(color_system="auto", markup=True)
_balcony_loggers = []


def clear_relations_cache() -> None:
    """Removes the `<service>.json` files."""
    relation_files = os.listdir(BALCONY_RELATIONS_DIR)
    deleted_filenames = []
    for rel_file in relation_files:
        if rel_file.endswith('.json'):
            rel_file_abs_path = os.path.join(BALCONY_RELATIONS_DIR, rel_file)
            if os.path.exists(rel_file_abs_path):
                os.remove(rel_file_abs_path)
                deleted_filenames.append(rel_file)
    return deleted_filenames


def get_rich_console() -> Console:
    """Returns the global defined `rich.console.Console` object for common use.

    Returns:
        rich.console.Console: rich console object
    """
    return _console


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
        handlers=[RichHandler(markup=True, console=_console)]
    )

    _logger = logging.getLogger(name)
    _balcony_loggers.append(_logger)
    return _logger
