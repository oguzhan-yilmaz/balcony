try:
    from ..nodes import ResourceNode
    from ..logs import get_logger
except ImportError:
    from nodes import ResourceNode
    from logs import get_logger
logger = get_logger(__name__)



class BuildsForProject(ResourceNode, service_name="codebuild", name="BuildsForProject"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def generate_jmespath_selector_from_relations(self, operation_name, relation_list):
        r = super().generate_jmespath_selector_from_relations(operation_name, relation_list)
        if operation_name == 'ListBuildsForProject':
            return '[].projects'
        return r

    def get_operations_relations(self, operation_name):
        r = super().get_operations_relations(operation_name)
        
        if operation_name == 'ListBuildsForProject':
            return [{
                "service_name": "codebuild",
                "resource_node_name": "BuildsForProject",
                "search_shape_name": "projectName",
                "target_shape_name": "projectName",
                "target_shape_type": "list",
                "operation_name": "ListProjects",
                "target_path": "[].projects"
            }
            ], FindRelationResultTypes.RelationsFound
        return r
        
