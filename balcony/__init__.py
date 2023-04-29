"""
The general export for the balcony's functionality.

Symbols exported in this file can be used in the following way:

```python
from balcony import BalconyAWS
```

Otherwise you'd need to specify the module name:

```python
from balcony.aws import BalconyAWS
```
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

# TODO: Fix this import mess
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
