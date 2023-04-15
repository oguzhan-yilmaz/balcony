from typing import List, Dict, Optional, Any
from pydantic import BaseModel, validator


class YamlRelation(BaseModel):
    service_name: str
    resource_node_name: str
    operation_name: str
    required_shape_name: str
    target_shape_name: str
    target_shape_type: str
    target_path: str


class YamlComplementApiParameterAction(BaseModel):
    _ACTION_TYPES = ("add", "remove")

    action: str
    data: Optional[Dict[str, Any]]
    keys: Optional[List[str]]

    @validator("action")
    def action_must_be_valid(cls, v):
        if v not in cls._ACTION_TYPES:
            raise ValueError("action must be 'add' or 'remove'")
        return v


class YamlResourceNodeOperation(BaseModel):
    operation_name: str
    jmespath_selector: Optional[str]
    complement_api_parameters: Optional[List[YamlComplementApiParameterAction]]
    explicit_relations: Optional[List[YamlRelation]]
    override_api_parameters: Optional[List[Dict[str, Any]]]
    pagination_token_mapping: Optional[Dict[str, str]]


class YamlServiceResourceNode(BaseModel):
    resource_node_name: str
    extra_relations: Optional[List[YamlRelation]]
    operations: Optional[List[YamlResourceNodeOperation]]


class YamlService(BaseModel):
    service_name: str
    resource_nodes: Optional[List[YamlServiceResourceNode]]

    # @validator("resource_node")
    # def validate_resource_node(cls, value):
    #     if not value.extra_relations and not value.operations:
    #         raise ValueError(
    #             "Either extra_relations or operations must be defined in resource_node"
    #         )
    #     return value
