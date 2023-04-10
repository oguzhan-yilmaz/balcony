from nodes import ResourceNode
from config import get_logger

logger = get_logger(__name__)

class Template(ResourceNode, service_name="ses", name="Template"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def define_extra_relations(self):
        return [{
            "service_name": "ses",
            "resource_node_name": "Template",
            "required_shape_name": "TemplateName",
            "target_shape_name": "Name",
            "target_shape_type": "string",
            "operation_name": "ListTemplates",
            "target_path": "TemplatesMetadata[*].Name"
        }]