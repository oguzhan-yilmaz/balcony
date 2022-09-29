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



class CodeBuild_BuildsForProject(ResourceNode, ResourceNodeRegistry, service_name="codebuild", name="BuildsForProject"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def generate_jmespath_selector_from_relations(self, operation_name, relation_list):
        r = super().generate_jmespath_selector_from_relations(operation_name, relation_list)
        if operation_name == 'ListBuildsForProject':
            return '[].projects'
        return r

    def get_operations_relations(self, operation_name, relation_map):
        r = super().get_operations_relations(operation_name, relation_map)
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
        
