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




class ECS_Cluster(ResourceNode, ResourceNodeRegistry, service_name="ecs", name="Clusters"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def generate_jmespath_selector_from_relations(self, operation_name, relation_list):
        r = super().generate_jmespath_selector_from_relations(operation_name, relation_list)
        if operation_name == 'ListClusters':
            return '[*].{cluster: clusterArns}[][]'
        return r
    
    def define_extra_relations(self):
        r= super().define_extra_relations()
        return [{
            "search_shape_name": "cluster",
            "target_shape_name": "cluster",
            "target_shape_type": "string",
            "operation_name": "ListClusters",
            "target_path": "clusterArns"
        }]
        
        
class ECS_Services(ResourceNode, ResourceNodeRegistry, service_name="ecs", name="Services"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_required_parameter_names_from_operation_name(self, operation_name):
        r = super().get_required_parameter_names_from_operation_name(operation_name)
        if operation_name == 'ListServices':
            return ['cluster']
        return r

    def get_operations_relations(self, operation_name, relation_map):
        r = super().get_operations_relations(operation_name, relation_map)
        if operation_name == 'DescribeServices':
            return [{
                "search_shape_name": "services",
                "target_shape_name": "serviceArns",
                "target_shape_type": "string",
                "operation_name": "ListServices",
                "target_path": "serviceArns"
            },
            {
                "search_shape_name": "cluster",
                "target_shape_name": "cluster",
                "target_shape_type": "string",
                "operation_name": "ListServices",
                "target_path": "__args__.cluster"
            }
            ]
        return r
    
    # def define_extra_relations(self):
    #     r= super().define_extra_relations()
   