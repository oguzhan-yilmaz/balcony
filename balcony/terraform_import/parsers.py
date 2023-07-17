from utils import find_all_yaml_files
from config import (
    get_logger,
    YAML_TF_IMPORT_CONFIGS_DIRECTORY,
    USER_DEFINED_YAML_TF_IMPORT_CONFIGS_DIRECTORY,
)
from terraform_import.models import (
    CustomTerraformImportConfigFile,
    # TerraformImportConfig,
)
from typing import Union, Tuple
import yaml
from collections import defaultdict

logger = get_logger(__name__)
_TERRAFORM_TYPES_KEY = "_terraform_types"


def parse_json_to_tf_import_config(
    input_configuration_dict: str,
) -> Union[bool, CustomTerraformImportConfigFile]:
    try:
        return CustomTerraformImportConfigFile(**input_configuration_dict)
    except Exception as e:
        logger.debug(f"Error while parsing user defined tf import config: {str(e)}")
    return False


def parse_yaml_file_to_tf_import_config(
    yaml_file_path: str,
) -> Tuple[CustomTerraformImportConfigFile, Union[Exception, None]]:
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
        return CustomTerraformImportConfigFile(**input_data), None
    except Exception as e:
        return False, e


def parse_custom_terraform_import_configs_from_files():
    terraform_configurations_dict = defaultdict(lambda: defaultdict(dict))

    parse_directories = [
        YAML_TF_IMPORT_CONFIGS_DIRECTORY,
    ]  # noqa
    _are_same_directories = (
        USER_DEFINED_YAML_TF_IMPORT_CONFIGS_DIRECTORY
        == YAML_TF_IMPORT_CONFIGS_DIRECTORY.as_posix()
    )
    if USER_DEFINED_YAML_TF_IMPORT_CONFIGS_DIRECTORY and not _are_same_directories:
        # might not be defined
        parse_directories.append(USER_DEFINED_YAML_TF_IMPORT_CONFIGS_DIRECTORY)

    for yaml_directory in parse_directories:
        config_filenames = find_all_yaml_files(yaml_directory)
        logger.debug(
            f"Terraform Import Configuration Registry: Found {len(config_filenames)} yaml files in {yaml_directory}. Starting to parse & validate them."
        )
        # parse them
        for conf_filename in config_filenames:
            conf, error = parse_yaml_file_to_tf_import_config(conf_filename)
            if error:
                logger.error(f"Error while parsing {conf_filename}: {error}")
                continue
            for tf_config in conf.import_configurations:
                # doing it this way allows overrides from the user defined configs
                r_node = terraform_configurations_dict.get(tf_config.service, {}).get(
                    tf_config.resource_node, False
                )
                if r_node is False:
                    terraform_configurations_dict[tf_config.service][
                        tf_config.resource_node
                    ] = [tf_config]
                else:
                    terraform_configurations_dict[tf_config.service][
                        tf_config.resource_node
                    ].append(tf_config)
                # add it to _TERRAFORM_TYPES_KEY
                tf_conf_list = terraform_configurations_dict[_TERRAFORM_TYPES_KEY].get(
                    tf_config.to_resource_type, []
                )
                if not tf_conf_list:
                    terraform_configurations_dict[_TERRAFORM_TYPES_KEY][
                        tf_config.to_resource_type
                    ] = [tf_config]
                else:
                    terraform_configurations_dict[_TERRAFORM_TYPES_KEY][
                        tf_config.to_resource_type
                    ].append(tf_config)
    return terraform_configurations_dict
