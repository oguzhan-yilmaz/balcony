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

class Lambda_Function(ResourceNode, ResourceNodeRegistry, service_name="lambda", name="Function"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def define_extra_relations(self):
        r= super().define_extra_relations()
        return [{
            "service_name": "lambda",
            "resource_node_name": "Function",
            "operation_name": "ListFunctions",
            "search_shape_name": "FunctionName",
            "target_shape_name": "FunctionName",
            "target_shape_type": "string",
            "target_path": "Functions[*].FunctionName"
        }]