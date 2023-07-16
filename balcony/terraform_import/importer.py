import re
import textwrap
from typing import Dict, List, Union
import jmespath
from terraform_import.models import TerraformImportConfig
from terraform_import.parsers import parse_custom_terraform_import_configs_from_files, _TERRAFORM_TYPES_KEY
from config import get_logger
from aws import BalconyAWS
from jinja2 import Environment

logger = get_logger(__name__)
_terraform_import_configurations = None


def get_custom_terraform_import_config_dict() -> Dict:
    global _terraform_import_configurations
    if _terraform_import_configurations:
        return _terraform_import_configurations

    _terraform_import_configurations = parse_custom_terraform_import_configs_from_files()
    return _terraform_import_configurations


def extract_resource_tags_as_kwargs(data: dict) -> dict:
    tags_as_kwargs = {}
    tag_list = data.get("Tags", [])
    if not tag_list or not isinstance(tag_list, list):
        return tags_as_kwargs

    for tag in tag_list:
        key = tag.get("Key")
        value = tag.get("Value")
        tags_as_kwargs[f"tag_{key}"] = value
    return tags_as_kwargs


def render_jinja2_template_with_data(data, jinja2_template_str) -> List[str]:
    template = Environment().from_string(jinja2_template_str)
    result = []
    # if the data is a dict, add the key-value pairs as kwargs
    if isinstance(data, dict):
        kwargs = data.copy()
        kwargs["data"] = data
        # if there's add it as tag_Name variable
        tags_as_kwargs = extract_resource_tags_as_kwargs(data)
        kwargs.update(tags_as_kwargs)
        rendered_output = template.render(**kwargs).strip()
        result.append(rendered_output)
    elif isinstance(data, list):
        # if the data is a list, render the template for each item
        kwargs = data.copy()
        for an_item in data:
            kwargs["item"] = an_item
            kwargs["data"] = an_item
            rendered_output = template.render(**kwargs).strip()
            result.append(rendered_output)
    elif isinstance(data, str):
        kwargs = {
            "item": data,
            "data": data,
        }
        rendered_output = template.render(**kwargs).strip()
        result.append(rendered_output)
    return result


def gen_resource_name_and_import_id_from_op_data_(
    operation_data, jmespath_query, to_resource_name_tpl, id_generator_tpl
):
    result = []
    if jmespath_query:
        # filter the operation data if jmespath_query is given
        # and render them one by one
        list_of_resource_data = jmespath.search(jmespath_query, operation_data)
        logger.debug(f"Filtered data using jmespath query: {jmespath_query}")

        for a_resource_data in list_of_resource_data:
            resource_name_list = render_jinja2_template_with_data(
                a_resource_data, to_resource_name_tpl
            )
            import_id_list = render_jinja2_template_with_data(
                a_resource_data, id_generator_tpl
            )
            result.extend(list(zip(resource_name_list, import_id_list)))

        return result
    else:
        # no jmespath query given, use the whole operation data
        # assumes there's multiple lines of output from the template

        resource_name_multiline = render_jinja2_template_with_data(
            a_resource_data, to_resource_name_tpl
        )[0]  # FIXME: later
        import_id_multiline = render_jinja2_template_with_data(
            a_resource_data, id_generator_tpl
        )[0]  # FIXME: later
        # split them on newlines
        resource_name_list = [ro for ro in resource_name_multiline.split("\n") if ro]
        import_id_list = [ro for ro in import_id_multiline.split("\n") if ro]

        logger.debug(f"{resource_name_list=}    {import_id_list=}")
        assert len(resource_name_list) == len(import_id_list)
        return list(zip(resource_name_list, import_id_list))


def generate_terraform_import_block(to_resource_type, to_resource_name, import_id):
    jinja_tmpl = textwrap.dedent(
        """
    import {
        to = {{ to_resource_type }}.{{ to_resource_name }}
        id = "{{ import_id }}"
    }
    """
    )

    jinja_env = Environment()
    template = jinja_env.from_string(jinja_tmpl)
    rendered_output = template.render(
        to_resource_type=to_resource_type,
        import_id=import_id,
        to_resource_name=to_resource_name,
    ).strip()
    return rendered_output


def get_importable_resources():
    custom_tf_config_dict = get_custom_terraform_import_config_dict()

    importable_services_and_resources = []
    for service_name, resource_config_dict in custom_tf_config_dict.items():
        for resource_node_name, resource_config in resource_config_dict.items():
            importable_services_and_resources.append((service_name, resource_node_name))
    return importable_services_and_resources


def sanitize_resource_name_and_import_ids(list_of_tuples):
    result = []
    for resource_name, import_id in list_of_tuples:
        # change anything that's not a letter, number, dash or underscore to underscore
        sanitized_resource_name = re.sub(r"[^A-Za-z0-9\-_]", "_", resource_name)

        if sanitized_resource_name and import_id:
            result.append((sanitized_resource_name, import_id))
    return result


def get_import_config_for(
    service: str = None,
    resource_node: str = None,
    terraform_resource_type: str = None,
) -> List[TerraformImportConfig]:
    custom_tf_config_dict = get_custom_terraform_import_config_dict()

    if service and resource_node:
        config_for_resource_node = custom_tf_config_dict.get(service, {}).get(
            resource_node, []
        )
        return config_for_resource_node
    elif terraform_resource_type:
        config_for_tf_type = custom_tf_config_dict.get(_TERRAFORM_TYPES_KEY, {}).get(
            terraform_resource_type, False
        )
        if not config_for_tf_type:
            return False
        return [config_for_tf_type]
    return False
    

def generate_import_block_from_import_config(
    balcony_client: BalconyAWS,
    tf_import_config: TerraformImportConfig,
    follow_pagination: bool = False
) -> List[str]:
    tf_import_blocks: List[str] = []

    operation_name = tf_import_config.operation_name
    service = tf_import_config.service
    resource_node = tf_import_config.resource_node
    jmespath_query = tf_import_config.jmespath_query

    if not tf_import_config:
        logger.debug(
            f"[red bold]No custom terraform import config found for {service}.{resource_node}. Please check out docs https://oguzhan-yilmaz.github.io/balcony/ for more info on developing it your own."
        )
        return False

    # read the operation
    operation_data = balcony_client.read_operation(
        service_name=service,
        resource_node_name=resource_node,
        operation_name=operation_name,
        follow_pagination=follow_pagination,
    )

    if not operation_data:
        logger.debug(f"No data found for {service}.{resource_node}.{operation_name}.")
        return False

    resource_name_and_import_ids = gen_resource_name_and_import_id_from_op_data_(
        operation_data,
        jmespath_query,
        tf_import_config.to_resource_name_jinja2_template,
        tf_import_config.id_generator_jinja2_template,
    )

    # Replace unsupported chars from the to-resource-name with underscore
    sanitized_resource_name_and_import_ids = sanitize_resource_name_and_import_ids(
        resource_name_and_import_ids
    )

    logger.debug(
        f"Found {len(sanitized_resource_name_and_import_ids)} resources to import."
    )
    for a_tuple in sanitized_resource_name_and_import_ids:
        to_resource_name, import_id = a_tuple
        tf_import_block = generate_terraform_import_block(
            tf_import_config.to_resource_type, to_resource_name, import_id
        )
        tf_import_blocks.append(tf_import_block)
    return tf_import_blocks



def generate_import_block_for_resource(
    balcony_client: BalconyAWS,
    service: str = None,
    resource_node: str = None,
    terraform_resource_type: str = None,
    follow_pagination: bool = False,
):
    resulting_tf_import_blocks = []
    tf_import_configs = get_import_config_for(service, resource_node, terraform_resource_type)
    if not tf_import_configs:
        logger.debug(
            f"[red bold]No custom terraform import config found for {service}.{resource_node}. Please check out docs https://oguzhan-yilmaz.github.io/balcony/ for more info on developing it your own."
        )
        return False

    for tf_import_config in tf_import_configs:
        tf_import_blocks = generate_import_block_from_import_config(balcony_client, tf_import_config, follow_pagination)
        if not tf_import_blocks:
            logger.debug(
                f"[red bold]No data found for {tf_import_config.to_resource_type} — {tf_import_config.resource_node}.{tf_import_config.operation_name}."
            )
            return False
        resulting_tf_import_blocks.extend(tf_import_blocks)
        
    return resulting_tf_import_blocks