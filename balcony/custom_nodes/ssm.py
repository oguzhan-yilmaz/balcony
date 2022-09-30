

try:
    from ..nodes import ResourceNode
    from ..registries import ResourceNodeRegistry
    from ..logs import get_logger
    from ..relations import FindRelationResultTypes, RelationMap
except ImportError:
    from nodes import ResourceNode
    from registries import ResourceNodeRegistry
    from logs import get_logger
    from relations import FindRelationResultTypes, RelationMap
logger = get_logger(__name__)



class SSM_Parameter(ResourceNode, ResourceNodeRegistry, service_name="ssm", name="Parameter"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def define_extra_relations(self):
        r= super().define_extra_relations()
        return [{
            "service_name": "ssm",
            "resource_node_name": "Parameter",
            "operation_name": "GetParameters",
            "search_shape_name": "Name",
            "target_shape_name": "Name",
            "target_shape_type": "string",
            "target_path": "Parameters[*].Name",
        }]
        
class SSM_ParameterHistory(ResourceNode, ResourceNodeRegistry, service_name="ssm", name="ParameterHistory"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def get_operations_relations(self, operation_name: str, relation_map: RelationMap = None):
        r = super().get_operations_relations(operation_name, relation_map)
        return [{
            "service_name": "ssm",
            "resource_node_name": "Parameter",
            "operation_name": "DescribeParameters",
            "search_shape_name": "Name",
            "target_shape_name": "Name",
            "target_shape_type": "string",
            "target_path": "Parameters[*].Name",
        }], FindRelationResultTypes.RelationsFound
    
    # def define_extra_relations(self):
    #     r= super().define_extra_relations()
    #     return [{
    #         "service_name": "ssm",
    #         "resource_node_name": "Parameter",
    #         "operation_name": "GetParameters",
    #         "search_shape_name": "Name",
    #         "target_shape_name": "Name",
    #         "target_shape_type": "string",
    #         "target_path": "Parameters[*].Name",
    #     }]