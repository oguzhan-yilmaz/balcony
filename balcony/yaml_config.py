from config import get_logger, YAML_IGNORE_PREFIX, YAML_SERVICES_DIRECTORY
from yaml_validators import YamlService
from utils import find_all_yaml_files
import yaml
from typing import List, Union, Tuple
from pathlib import Path


logger = get_logger(__name__)


def parse_yaml_file_to_service(
    yaml_file_path: str,
) -> Tuple[YamlService, Union[Exception, None]]:
    """Parses given YAML file and returns a pydantic model: YamlService object

    Args:
        yaml_file_path (str): Filepath for the yaml file

    Returns:
        YamlService: Input data parsed as a pydantic YamlService object
        Exception or `None`: Exception if raised during parsing, or None if successful
    """
    try:
        with open(yaml_file_path, "r") as f:
            input_data = yaml.load(f, Loader=yaml.FullLoader)
        return YamlService(**input_data), None
    except Exception as e:
        logger.debug(f"Failed to parse yaml file {yaml_file_path}. Error: {str(e)}")
        return False, e


def find_and_parse_yaml_services() -> List[YamlService]:
    """Searches and finds the defined yaml files in the YAML_SERVICES_DIRECTORY directory that are not starting with '_'

    Returns:
        List[YamlService]: List of found YamlServices, created from yaml files
    """
    found_yaml_services = []
    yaml_files = find_all_yaml_files(YAML_SERVICES_DIRECTORY)
    logger.debug(
        f"Terraform Import Configuration Registry: Found {len(yaml_files)} yaml files in {YAML_SERVICES_DIRECTORY}. Starting to parse & validate them."
    )
    for yaml_file in yaml_files:
        yaml_service, error = parse_yaml_file_to_service(yaml_file)
        if error is None and yaml_service:
            logger.debug(f"Succesfully parsed [bold]{yaml_file}[/] to Yaml ResourceNode")
            found_yaml_services.append(yaml_service)
        else:
            logger.debug(
                f"Failed to parse [bold]{yaml_file}[/] to service. Error: {str(error)}. "
            )

    return found_yaml_services


def _test_example_service_yaml():
    example_service_filepath = (
        Path(__file__).parent / "custom_nodes" / "yamls" / "_example_service.yaml"
    )
    # Load input data from YAML
    service = parse_yaml_file_to_service(example_service_filepath)
    print(service)


if __name__ == "__main__":
    _test_example_service_yaml()
