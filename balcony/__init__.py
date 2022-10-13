"""
Any resource that app system is going to use must be exported here.
Otherwise different import statements would create new global static objects
for AppRegistry etc.
"""
try:
    from .registries import app_registry, AppRegistry
    from .app import BaseBalconyApp
    from .factories import BalconyAWS
    from .logs import get_rich_console, get_logger
except ImportError:
    from registries import app_registry, AppRegistry
    from app import BaseBalconyApp
    from factories import BalconyAWS
    from logs import get_rich_console, get_logger
