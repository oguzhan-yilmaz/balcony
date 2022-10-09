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



class IAM_Policy(ResourceNode, ResourceNodeRegistry, service_name="iam", name="Policy"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def define_extra_relations(self):
        r= super().define_extra_relations()
        return [{
            "service_name": "iam",
            "resource_node_name": "Policy",
            "search_shape_name": "PolicyArn",
            "target_shape_name": "Arn",
            "target_shape_type": "string",
            "operation_name": "ListPolicies",
            "target_path": "Policies[*].Arn"
        }]

class IAM_User(ResourceNode, ResourceNodeRegistry, service_name="iam", name="User"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def define_extra_relations(self):
        r= super().define_extra_relations()
        return [{
                "service_name": "iam",
            "resource_node_name": "User",
            "search_shape_name": "UserName",
            "target_shape_name": "UserName",
            "target_shape_type": "string",
            "operation_name": "ListUsers",
            "target_path": "Users[*].UserName"
        }]

class IAM_Role(ResourceNode, ResourceNodeRegistry, service_name="iam", name="Role"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def define_extra_relations(self):
        r= super().define_extra_relations()
        return [{
            "service_name": "iam",
            "resource_node_name": "Role",
            "search_shape_name": "RoleName",
            "target_shape_name": "RoleName",
            "target_shape_type": "string",
            "operation_name": "ListRoles",
            "target_path": "Roles[*].RoleName"
        }]
    
class IAM_AccessKeys(ResourceNode, ResourceNodeRegistry, service_name="iam", name="AccessKeys"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def define_extra_relations(self):
        r= super().define_extra_relations()
        return [{
            "service_name": "iam",
            "resource_node_name": "AccessKeys",
            "search_shape_name": "AccessKeyId",
            "target_shape_name": "AccessKeyId",
            "target_shape_type": "string",
            "operation_name": "ListAccessKeys",
            "target_path": "AccessKeyMetadata[*].AccessKeyId"
        }]
        