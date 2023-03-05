"""
Any resource that app system is going to use must be exported here.
Otherwise different import statements would create new global static objects
for AppRegistry etc.
"""
try:
    from .aws import BalconyAWS, Boto3SessionSingleton
    from .config import get_rich_console, get_logger
    from .nodes import ServiceNode, ResourceNode
    from .reader import ServiceReader
    from .relations import RelationMap
    from .errors import Error
except ImportError:
    from balcony.aws import BalconyAWS, Boto3SessionSingleton
    from config import get_rich_console, get_logger
    from nodes import ServiceNode, ResourceNode
    from reader import ServiceReader
    from relations import RelationMap
    from errors import Error
