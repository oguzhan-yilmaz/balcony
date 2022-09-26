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

# class EC2_Vpc(ResourceNode, ResourceNodeRegistry, service_name="ec2", name="Vpc"):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # print("VPC init")


# class EC2_Instance(ResourceNode, ResourceNodeRegistry, service_name="ec2", name="Instance"):
#     def get_parameter_aliases_of_operation(self, operation_name):
#         result = super().get_parameter_aliases_of_operation(operation_name)
#         return result
        # print("Instance init")

class EC2_SecurityGroups(ResourceNode, ResourceNodeRegistry, service_name="ec2", name="SecurityGroups"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def find_best_relations_for_operation(self, operation_name, relation_map):
        r = super().find_best_relations_for_operation(operation_name, relation_map)
        
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
class S3_BucketLifecycleConfiguration(ResourceNode, ResourceNodeRegistry, service_name="s3", name="BucketLifecycleConfiguration"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def define_extra_relations(self):
        r= super().define_extra_relations()
        return [{
            "search_shape_name": "Bucket",
            "target_shape_name": "Name",
            "target_shape_type": "string",
            "operation_name": "ListBuckets",
            "target_path": "Buckets[*].Name"
        }]

    # def find_best_relations_for_operation(self, operation_name, relation_map):
    #     r = super().find_best_relations_for_operation(operation_name, relation_map)
    #     return r
    
    def _generate_jmespath_selector_from_relations(self, operation_name, relation_list):
        r = super()._generate_jmespath_selector_from_relations(operation_name, relation_list)
        return r
    
    def create_valid_api_parameters_list(self, operation_name, raw_api_parameters_list, relations_of_operation):
        r = super().create_valid_api_parameters_list(operation_name, raw_api_parameters_list, relations_of_operation)
        return r
    
class IAM_Policy(ResourceNode, ResourceNodeRegistry, service_name="iam", name="Policy"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def define_extra_relations(self):
        r= super().define_extra_relations()
        return [{
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
            "search_shape_name": "AccessKeyId",
            "target_shape_name": "AccessKeyId",
            "target_shape_type": "string",
            "operation_name": "ListAccessKeys",
            "target_path": "AccessKeyMetadata[*].AccessKeyId"
        }]
        
class ECS_Cluster(ResourceNode, ResourceNodeRegistry, service_name="ecs", name="Clusters"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def _generate_jmespath_selector_from_relations(self, operation_name, relation_list):
        r = super()._generate_jmespath_selector_from_relations(operation_name, relation_list)
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

    def find_best_relations_for_operation(self, operation_name, relation_map):
        r = super().find_best_relations_for_operation(operation_name, relation_map)
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
   

class CodeBuild_BuildsForProject(ResourceNode, ResourceNodeRegistry, service_name="codebuild", name="BuildsForProject"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _generate_jmespath_selector_from_relations(self, operation_name, relation_list):
        r = super()._generate_jmespath_selector_from_relations(operation_name, relation_list)
        if operation_name == 'ListBuildsForProject':
            return '[].projects'
        return r

    def find_best_relations_for_operation(self, operation_name, relation_map):
        r = super().find_best_relations_for_operation(operation_name, relation_map)
        if operation_name == 'ListBuildsForProject':
            return [{
                "search_shape_name": "projectName",
                "target_shape_name": "projectName",
                "target_shape_type": "list",
                "operation_name": "ListProjects",
                "target_path": "[].projects"
            }
            ], FindRelationResultTypes.RelationsFound
        return r
        
class Lambda_Function(ResourceNode, ResourceNodeRegistry, service_name="lambda", name="Function"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def define_extra_relations(self):
        r= super().define_extra_relations()
        return [{
            "search_shape_name": "FunctionName",
            "target_shape_name": "FunctionName",
            "target_shape_type": "string",
            "operation_name": "ListFunctions",
            "target_path": "Functions[*].FunctionName"
        }]