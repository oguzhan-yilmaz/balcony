from nodes import ResourceNode
from config import get_logger

logger = get_logger(__name__)

class BucketLifecycleConfiguration(ResourceNode, service_name="s3", name="BucketLifecycleConfiguration"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def define_extra_relations(self):
        r= super().define_extra_relations()
        return [{
            "service_name": "s3",
            "resource_node_name": "Buckets",
            "required_shape_name": "Bucket",
            "target_shape_name": "Name",
            "target_shape_type": "string",
            "operation_name": "ListBuckets",
            "target_path": "Buckets[*].Name"
        }]

    # def find_best_relations_for_operation(self, operation_name, relation_map):
    #     r = super().find_best_relations_for_operation(operation_name, relation_map)
    #     return r
    
    def generate_jmespath_selector_from_relations(self, operation_name, relation_list):
        r = super().generate_jmespath_selector_from_relations(operation_name, relation_list)
        return r
