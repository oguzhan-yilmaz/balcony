"""
Any resource that app system is going to use must be exported here.
Otherwise different import statements would create new global static objects
for AppRegistry etc.
"""
try:
    from .factories import BalconyAWS
    from .config import get_rich_console, get_logger
except ImportError:
    from factories import BalconyAWS
    from config import get_rich_console, get_logger
