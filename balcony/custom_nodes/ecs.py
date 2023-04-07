# from ..nodes import ResourceNode
# from ..config import get_logger

# logger = get_logger(__name__)



# class Cluster(ResourceNode, service_name="ecs", name="Clusters"):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
    
#     def generate_jmespath_selector_from_relations(self, operation_name, relation_list):
#         r = super().generate_jmespath_selector_from_relations(operation_name, relation_list)
#         if operation_name == 'ListClusters':
#             return '[*].{cluster: clusterArns}[][]'
#         return r
    
#     # def define_extra_relations(self):
#     #     r= super().define_extra_relations()
#     #     return [{
#     #         "service_name": "ecs",
#     #         "resource_node_name": "Clusters",
#     #         "required_shape_name": "cluster",
#     #         "target_shape_name": "cluster",
#     #         "target_shape_type": "string",
#     #         "operation_name": "ListClusters",
#     #         "target_path": "clusterArns"
#     #     }]
        

# class Tasks(ResourceNode, service_name="ecs", name="Tasks"):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#     def get_required_parameter_names_from_operation_name(self, operation_name):
#         r = super().get_required_parameter_names_from_operation_name(operation_name)
#         if operation_name == 'DescribeTasks':
#             return ['tasks']
#         if operation_name == 'ListTasks':
#             return ['cluster']
#         return r
    
#     # def define_extra_relations(self):
#     #     return [
#     #         {
#     #             "service_name": "ecs",
#     #             "resource_node_name": "Tasks",
#     #             "required_shape_name": "tasks",
#     #             "target_shape_name": "taskArns",
#     #             "target_shape_type": "string",
#     #             "operation_name": "ListTasks",
#     #             "target_path": "taskArns"
#     #         }
#     #     ]
     
# class Services(ResourceNode, service_name="ecs", name="Services"):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#     def get_required_parameter_names_from_operation_name(self, operation_name):
#         r = super().get_required_parameter_names_from_operation_name(operation_name)
#         if operation_name == 'ListServices':
#             return ['cluster']
#         return r
    
#     def generate_jmespath_selector_from_relations(self, operation_name, relation_list) -> str:
#         if operation_name == 'ListServices':
#             return "[*].clusterArns[].{cluster: @}"
#         if operation_name == 'DescribeServices':
#             return "[*].serviceArns[].{services: [@]}"
        
#         return super().generate_jmespath_selector_from_relations(operation_name, relation_list)

    
#     def define_extra_relations(self):
#         return [
#             {
#                 "service_name": "ecs",
#                 "resource_node_name": "Services",
#                 "required_shape_name": "services",
#                 "target_shape_name": "serviceArns",
#                 "target_shape_type": "string",
#                 "operation_name": "ListServices",
#                 "target_path": "[*].serviceArns"
#             },
#             {
#                 "service_name": "ecs",
#                 "resource_node_name": "Clusters",
#                 "required_shape_name": "cluster",
#                 "target_shape_name": "cluster",
#                 "target_shape_type": "string",
#                 "operation_name": "ListClusters",
#                 "target_path": "[*].clusterArns"
#             }
#         ]

#     # def get_operations_relations(self, operation_name):
#     #     r = super().get_operations_relations(operation_name)
#     #     if operation_name == 'DescribeServices':
#     #         return [
#     #         #     {
#     #         #     "service_name": "ecs",
#     #         #     "resource_node_name": "Services",
#     #         #     "required_shape_name": "services",
#     #         #     "target_shape_name": "serviceArns",
#     #         #     "target_shape_type": "string",
#     #         #     "operation_name": "ListServices",
#     #         #     "target_path": "serviceArns"
#     #         # },
#     #         {
#     #             "service_name": "ecs",
#     #             "resource_node_name": "Services",
#     #             "required_shape_name": "cluster",
#     #             "target_shape_name": "cluster",
#     #             "target_shape_type": "string",
#     #             "operation_name": "ListClusters",
#     #             "target_path": "[*].clusterArns"
#     #         }
#     #         ], None
#     #     return r
    
#     # def define_extra_relations(self):
#     #     r= super().define_extra_relations()
   