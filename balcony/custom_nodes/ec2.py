try:
    from ..nodes import ResourceNode
    from ..registries import ResourceNodeRegistry
    from ..logs import get_logger
    from ..relations import FindRelationResultTypes
except ImportError:
    from nodes import ResourceNode
    from registries import ResourceNodeRegistry
    from logs import get_logger
    from relations import FindRelationResultTypes
logger = get_logger(__name__)


class EC2_SecurityGroups(ResourceNode, ResourceNodeRegistry, service_name="ec2", name="SecurityGroups"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def get_operations_relations(self, operation_name, relation_map):
        r = super().get_operations_relations(operation_name, relation_map)
        
"""
1. check for already existing operation data
2. get relations of the operation
3. find the dependent operations to call
4. read the target dependent operation
5. generate JMESpath selectors with the relations
6. search with JMESpath to get raw_parameters
7. generate real api parameters from raw_parameters
8. read the current operation
"""
