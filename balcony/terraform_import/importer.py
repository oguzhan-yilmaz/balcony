import re
import textwrap
from typing import List
import jmespath
from terraform_import.parsers import parse_custom_tf_import_config
from config import get_logger
from aws import BalconyAWS
from jinja2 import Environment

logger = get_logger(__name__)


def generate_import_id_list(data, id_generator_tpl):
    template = Environment().from_string(id_generator_tpl)
    rendered_output = template.render(data=data, **data).strip()
    # import_id_list = [ro for ro in rendered_output.split("\n") if ro]
    # return import_id_list
    return rendered_output


def generate_to_resource_name_list(data, resource_name_generator_tpl):
    to_resource_node_template = Environment().from_string(resource_name_generator_tpl)
    rendered_output = to_resource_node_template.render(data=data, **data).strip()
    # to_resource_name_list = [ro for ro in rendered_output.split("\n") if ro]
    # return to_resource_name_list
    return rendered_output


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
            resource_name = generate_to_resource_name_list(
                a_resource_data, to_resource_name_tpl
            )
            import_id = generate_import_id_list(a_resource_data, id_generator_tpl)
            result.append((resource_name, import_id))
        return result
    else:
        # no jmespath query given, use the whole operation data

        resource_name_multiline = generate_to_resource_name_list(
            a_resource_data, to_resource_name_tpl
        )
        import_id_multiline = generate_import_id_list(a_resource_data, id_generator_tpl)
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
    ).lstrip()

    jinja_env = Environment()
    template = jinja_env.from_string(jinja_tmpl)
    rendered_output = template.render(
        to_resource_type=to_resource_type,
        import_id=import_id,
        to_resource_name=to_resource_name,
    ).strip()
    return rendered_output


def generate_import_block_for_resource(
    balcony_client: BalconyAWS,
    service: str,
    resource_node: str,
    follow_pagination: bool = False,
):

    tf_import_blocks: List[str] = []
    custom_tf_config_dict = parse_custom_tf_import_config()
    config_for_resource_node = custom_tf_config_dict.get(service, {}).get(
        resource_node, False
    )
    if not config_for_resource_node:
        logger.debug(
            f"No custom terraform import config found for {service}/{resource_node}."
        )
        return False

    # read the data
    operation_name = config_for_resource_node.operation_name

    jmespath_query = config_for_resource_node.jmespath_query

    operation_data = balcony_client.read_operation(
        service_name=service,
        resource_node_name=resource_node,
        operation_name=operation_name,
        follow_pagination=follow_pagination,  # TODO: remove the comment after
    )

    if not operation_data:
        logger.debug("No data found for {service}/{resource_node}/{operation_name}.")
        return False

    resource_name_and_import_ids = gen_resource_name_and_import_id_from_op_data_(
        operation_data,
        jmespath_query,
        config_for_resource_node.to_resource_name_jinja2_template,
        config_for_resource_node.id_generator_jinja2_template,
    )

    def sanitize_resource_name_and_import_ids(list_of_tuples):
        result = []
        for resource_name, import_id in list_of_tuples:
            # change anything that's not a letter, number, dash or underscore to underscore
            sanitized_resource_name = re.sub(r"[^A-Za-z0-9\-_]", "_", resource_name)

            if sanitized_resource_name and import_id:
                result.append((sanitized_resource_name, import_id))
        return result

    sanitized_resource_name_and_import_ids = sanitize_resource_name_and_import_ids(
        resource_name_and_import_ids
    )

    logger.debug(
        f"Found {len(sanitized_resource_name_and_import_ids)} resources to import."
    )
    for a_tuple in sanitized_resource_name_and_import_ids:
        to_resource_name, import_id = a_tuple
        tf_import_block = generate_terraform_import_block(
            config_for_resource_node.to_resource_type, to_resource_name, import_id
        )
        tf_import_blocks.append(tf_import_block)
    return tf_import_blocks
