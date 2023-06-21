from typing import List, Dict, Optional, Any
from pydantic import BaseModel, validator


class TerraformImportConfig(BaseModel):
    service: str  # ec2
    resource_node: str  # Instances
    operation_name: str  # DescribeInstances
    jmespath_query: Optional[str]  # Reservations[].Instances[]
    to_resource_type: str  # aws_instance
    to_resource_name_jinja2_template: str  # "{{ .InstanceId }}"
    id_generator_jinja2_template: str  # "{{ .InstanceId }}"

    # TODO: create validators


class MaintainersBlock(BaseModel):
    name: str
    github: Optional[str]
    email: Optional[str]


class CustomTerraformImportConfigFile(BaseModel):
    maintainers: Optional[MaintainersBlock]
    import_configurations: List[TerraformImportConfig]
