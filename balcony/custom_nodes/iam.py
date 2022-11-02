try:
    from ..nodes import ResourceNode
    from ..logs import get_logger
    from ..errors import Error
except ImportError:
    from nodes import ResourceNode
    from logs import get_logger
    from errors import Error

logger = get_logger(__name__)
from typing import List, Set, Dict, Tuple, Optional, Union



class Policy(ResourceNode, service_name="iam", name="Policy"):
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
        },
        {
            "service_name": "iam",
            "resource_node_name": "Policy",
            "search_shape_name": "VersionId",
            "target_shape_name": "DefaultVersionId",
            "target_shape_type": "string",
            "operation_name": "ListPolicies",
            "target_path": "Policies[*].DefaultVersionId"
        }]
        
    
    def generate_api_parameters_from_operation_data(self, operation_name:str, 
                                                    relations_of_operation:List[Dict], 
                                                    related_operations_data: Union[List, Dict]) -> Tuple[Union[List, bool], Union[Error, None]]:
        generated_api_parameters, err = super().generate_api_parameters_from_operation_data(operation_name, relations_of_operation, related_operations_data)

        if err is not None:
            return generated_api_parameters, err
        
        if operation_name == "ListPolicies":
            api_parameters = []
            for api_param in generated_api_parameters:
                api_param.update({'Scope':'Local'})
                api_parameters.append(api_param)
            return api_parameters, None
            
        return generated_api_parameters, err
            

class User(ResourceNode, service_name="iam", name="User"):
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

class Role(ResourceNode, service_name="iam", name="Role"):
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
    
class AccessKeys(ResourceNode, service_name="iam", name="AccessKeys"):
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
        