from typing import List, Dict, Optional, Any
from pydantic import BaseModel, validator
import yaml


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


# Load input data from YAML
def test_service_yaml():
    input_yaml = """
    service_name: ec2
    resource_nodes:
    - resource_node_name: Instance
    extra_relations:
        - service_name: x
        resource_node_name: y 
        operation_name: z
        required_shape_name: a 
        target_shape_name: b
        target_shape_type: c
        target_path: d
    operations:
        - operation_name: ListOperation
        jmespath_selector: "[].example"
        complement_api_parameters:
            - action: add
            data:
                any: data
                is: fine
            - action: remove
            keys:
                - aa
                - bb
        explicit_relations:
            - service_name: x
            resource_node_name: y
            operation_name: z
            required_shape_name: a
            target_shape_name: b
            target_shape_type: c
            target_path: d
            - service_name: x1
            resource_node_name: y1
            operation_name: z1
            required_shape_name: a1
            target_shape_name: b1
            target_shape_type: c1
            target_path: d1
        override_api_parameters:
            - param1: arg1
            param2: param2
            param3: arg3
    """
    input_data = yaml.safe_load(input_yaml)

    # Validate input data using the Service model
    service = YamlService(**input_data)
    print(service)
