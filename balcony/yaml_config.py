from config import get_logger, YAML_IGNORE_PREFIX, YAML_SERVICES_DIRECTORY
from yaml_validators import YamlService

import yaml
import os
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
        return False, e


def find_all_yaml_files(directory: str) -> List[str]:
    """Find all yaml files in a directory with the exception of files starting with "_".

    Args:
        directory (str): Directory to search for yaml files

    Returns:
        List[str]: List of yaml file paths
    """
    yaml_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            # support any yaml file with the exception of files starting with "YAML_IGNORE_PREFIX"
            if file.endswith(".yaml") and not file.startswith(YAML_IGNORE_PREFIX):
                yaml_files.append(os.path.join(root, file))
    return yaml_files


def find_and_parse_yaml_services() -> List[YamlService]:
    """Searches and finds the defined yaml files in the YAML_SERVICES_DIRECTORY directory that are not starting with '_'

    Returns:
        List[YamlService]: List of found YamlServices, created from yaml files
    """
    found_yaml_services = []
    yaml_files = find_all_yaml_files(YAML_SERVICES_DIRECTORY)
    logger.debug(
        f"Found {len(yaml_files)} yaml files in {YAML_SERVICES_DIRECTORY}. Starting to parse & validate them."
    )
    for yaml_file in yaml_files:
        yaml_service, error = parse_yaml_file_to_service(yaml_file)
        if error is None and yaml_service:
            found_yaml_services.append(yaml_service)
        else:
            logger.debug(
                f"Failed to parse [bold]{yaml_file}[/] to service. Error: {str(error)}. "
            )

    return found_yaml_services


# Load input data from YAML
def _test_example_service_yaml():
    example_service_filepath = (
        Path(__file__).parent / "custom_nodes" / "yamls" / "_example_service.yaml"
    )
    service = parse_yaml_file_to_service(example_service_filepath)
    print(service)


if __name__ == "__main__":
    _test_example_service_yaml()
