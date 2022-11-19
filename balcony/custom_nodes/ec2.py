try:
    from ..nodes import ResourceNode
    from ..config import get_logger
except ImportError:
    from nodes import ResourceNode
    from config import get_logger
logger = get_logger(__name__)


class SecurityGroups(ResourceNode, service_name="ec2", name="SecurityGroups"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
