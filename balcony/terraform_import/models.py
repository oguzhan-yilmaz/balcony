from typing import List, Optional
from pydantic import BaseModel  # , validator


class TerraformImportConfig(BaseModel):
    service: str  # ec2
    resource_node: str  # Instances
    operation_name: str  # DescribeInstances
    jmespath_query: Optional[str]  # Reservations[].Instances[]
    to_resource_type: str  # aws_instance
    to_resource_name_jinja2_template: str  # "{{ InstanceId }}"
    id_generator_jinja2_template: str
    multiline_output: Optional[bool]

    # TODO: code the validators
    # @validator("to_resource_name_jinja2_template")
    # def validate_to_resource_name_jinja2_template(cls, value):
    #     # Add your validation logic here
    #     # You can raise a ValueError if the value is invalid
    #     return value

    # @validator("id_generator_jinja2_template")
    # def validate_id_generator_jinja2_template(cls, value):
    #     # Add your validation logic here
    #     # You can raise a ValueError if the value is invalid
    #     return value


class MaintainersBlock(BaseModel):
    """List of maintainers for the terraform import config file."""

    name: str
    github: Optional[str]
    email: Optional[str]


class CustomTerraformImportConfigFile(BaseModel):
    maintainers: Optional[List[MaintainersBlock]]
    import_configurations: List[TerraformImportConfig]
