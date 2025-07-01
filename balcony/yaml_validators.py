from typing import List, Dict, Optional, Any
from pydantic import BaseModel, field_validator


class YamlRelation(BaseModel):
    service_name: str
    resource_node_name: str
    operation_name: str
    required_shape_name: str
    target_shape_name: Optional[str] = None
    target_shape_type: Optional[str] = None
    target_path: Optional[str] = None


class YamlComplementApiParameterAction(BaseModel):
    """Defines the `add` and `remove` options for complement_api_parameters in YamlResourceNodeOperation"""

    _ACTION_TYPES = ("add", "remove")

    action: str
    data: Optional[Dict[str, Any]] = None
    keys: Optional[List[str]] = None

    @field_validator("action")
    @classmethod
    def action_must_be_valid(cls, v):
        """Validates the action field. Must be 'add' or 'remove'"""
        if v not in cls._ACTION_TYPES:
            raise ValueError("action must be 'add' or 'remove'")
        return v


class YamlResourceNodeOperation(BaseModel):
    """Defines the customizations for a specific operation in a Resource Node."""

    operation_name: str
    jmespath_selector: Optional[str] = None
    complement_api_parameters: Optional[List[YamlComplementApiParameterAction]] = None
    explicit_relations: Optional[List[YamlRelation]] = None
    override_api_parameters: Optional[List[Dict[str, Any]]] = None
    pagination_token_mapping: Optional[Dict[str, str]] = None
    required_parameters: Optional[List[str]] = None


class YamlServiceResourceNode(BaseModel):
    """Defines a Resource Node in a Service. It can have extra_relations and list of operations"""

    resource_node_name: str
    extra_relations: Optional[List[YamlRelation]] = None
    operations: Optional[List[YamlResourceNodeOperation]] = None


class YamlService(BaseModel):
    """Defines a Service in a Yaml file. It can have multiple Resource Nodes"""

    service_name: str
    resource_nodes: Optional[List[YamlServiceResourceNode]] = None

    # @field_validator("resource_node")
    # @classmethod
    # def validate_resource_node(cls, value):
    #     if not value.extra_relations and not value.operations:
    #         raise ValueError(
    #             "Either extra_relations or operations must be defined in resource_node"
    #         )
    #     return value
