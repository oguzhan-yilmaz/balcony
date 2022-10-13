import logging
from rich.logging import RichHandler
from rich.console import Console

try:
    from .settings import LOG_LEVEL
except ImportError:
    from settings import LOG_LEVEL
    
_console = Console()
_balcony_loggers = []

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
        name (str): Logger name. Usually `__name__`.

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
    
    _logger = logging.getLogger(name)
    _balcony_loggers.append(_logger)
    return _logger
