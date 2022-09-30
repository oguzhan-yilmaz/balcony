"""
When a Python module is imported as `from <module> import *`,
modules `__init__.py` file is imported.  

"""

from .ec2 import *
from .codebuild import *
from .ecs import *
from .lambda_functions import *
from .iam import *
from .ssm import *
from .s3 import *