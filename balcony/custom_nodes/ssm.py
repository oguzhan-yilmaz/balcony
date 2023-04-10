from nodes import ResourceNode
from config import get_logger

logger = get_logger(__name__)



class Parameter(ResourceNode, service_name="ssm", name="Parameter"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def define_extra_relations(self):
        r= super().define_extra_relations()
        return [{
            "service_name": "ssm",
            "resource_node_name": "Parameter",
            "operation_name": "GetParameters",
            "required_shape_name": "Name",
            "target_shape_name": "Name",
            "target_shape_type": "string",
            "target_path": "Parameters[*].Name",
        }]
        
class ParameterHistory(ResourceNode, service_name="ssm", name="ParameterHistory"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def get_operations_relations(self, operation_name: str):
        r = super().get_operations_relations(operation_name)
        return [{
            "service_name": "ssm",
            "resource_node_name": "Parameter",
            "operation_name": "DescribeParameters",
            "required_shape_name": "Name",
            "target_shape_name": "Name",
            "target_shape_type": "string",
            "target_path": "Parameters[*].Name",
        }], None
    
