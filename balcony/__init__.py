"""
Any resource that app system is going to use must be exported here.
Otherwise different import statements would create new global static objects
for AppRegistry etc.
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

try:
    from .aws import BalconyAWS
    from .config import get_rich_console, get_logger
    from .nodes import ServiceNode, ResourceNode
    from .reader import ServiceReader
    from .relations import RelationMap
    from .errors import Error
except ImportError:
    # print('ImportError: balcony/__init__.py')
    from aws import BalconyAWS
    from config import get_rich_console, get_logger
    from nodes import ServiceNode, ResourceNode
    from reader import ServiceReader
    from relations import RelationMap
    from errors import Error
