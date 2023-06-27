import os
import random
import string
import textwrap
from typing import List, Union
import jmespath
import yaml
from terraform_import.importer import render_jinja2_template_with_data
from terraform_import.parsers import parse_json_to_tf_import_config
from config import (
    get_logger,
    get_rich_console,
    USER_DEFINED_YAML_TF_IMPORT_CONFIGS_DIRECTORY,
)
from aws import BalconyAWS
from rich.prompt import Prompt, Confirm
import typer
from botocore.utils import ArgumentGenerator
from rich.panel import Panel
from rich.padding import Padding
from rich.pretty import Pretty
from rich.syntax import Syntax

logger = get_logger(__name__)
console = get_rich_console()


def get_operation_names_of_a_resource(
    balcony_aws: BalconyAWS, service: str, resource_name: str
):
    service_node = balcony_aws.get_service_node(service)
    if not service_node:
        return False
    resource_node = service_node.get_resource_node_by_name(resource_name)
    if not resource_node:
        return False
    operation_names = resource_node.operation_names
    return operation_names


def get_documentation_panel_for_operation(
    balcony_aws: BalconyAWS, service: str, resource_name: str, operation_name: str
):
    service_node = balcony_aws.get_service_node(service)
    if not service_node:
        return False
    resource_node = service_node.get_resource_node_by_name(resource_name)
    if not resource_node:
        return False
    operation_docs_panel = resource_node._rich_operation_details_panel(
        operation_name, remove_input_shape=True, remove_documentation=True
    )
    return operation_docs_panel


def get_operation_model_for_operation(
    balcony_aws: BalconyAWS, service: str, resource_name: str, operation_name: str
):
    service_node = balcony_aws.get_service_node(service)
    if not service_node:
        return False
    resource_node = service_node.get_resource_node_by_name(resource_name)
    if not resource_node:
        return False
    operation_model = resource_node.get_operation_model(operation_name)
    return operation_model


def gen_mock_output_data_for_operation(
    balcony_aws, service, resource_name, operation_name
):
    arg_gen = ArgumentGenerator(use_member_names=True)
    op_model = get_operation_model_for_operation(
        balcony_aws, service, resource_name, operation_name
    )
    mock_output_data = arg_gen.generate_skeleton(op_model.output_shape)

    return mock_output_data


def gen_balcony_tf_import_config_yaml(user_def_import_configuration_list: List[dict]):
    yaml_dict = {
        "maintainers": [{"name": "Your Name"}],
        "import_configurations": user_def_import_configuration_list,
    }

    parsed = parse_json_to_tf_import_config(yaml_dict)
    if not parsed:
        return False

    yaml_output = yaml.dump(yaml_dict)
    return yaml_output


def generate_google_search_uri(keywords):
    search_terms = "+".join(keywords)
    return f"https://www.google.com/search?q={search_terms}"


def save_tf_input_config_to_user_defined_yaml_dir(filename: str, yaml_content: str):
    if not USER_DEFINED_YAML_TF_IMPORT_CONFIGS_DIRECTORY:
        return False

    filepath = os.path.join(USER_DEFINED_YAML_TF_IMPORT_CONFIGS_DIRECTORY, filename)

    with open(filepath, "w") as f:
        f.write(yaml_content)

    return filepath


def interactive_help(balcony_aws: BalconyAWS, service: str, resource_name: str):
    console.print(
        Padding(
            Panel(  # noqa
                textwrap.dedent(
                    f"""
                Welcome to the Balcony interactive help for generating Terraform import configurations for AWS Services.
                
                You'll be asked a series of questions to help you generate the configuration.                        
                """
                ),  # noqa
                title="[bold blue]Balcony Interactive Help - Generate Terraform Import Configurations",
            ),
            (1, 2),
        ),
    )

    operation_names = get_operation_names_of_a_resource(
        balcony_aws, service, resource_name
    )
    if not operation_names:
        console.print(
            f"[red bold]No operations found for {service}.{resource_name}[/red bold]"
        )
        raise typer.Exit(1)

    console.print()
    console.rule("[bold cyan underline]Operation Selection")
    console.print()
    console.print("balcony may have multiple Operations for a Resource.")
    console.print(
        "Select which operation to use for generating the import configuration."
    )
    console.print(
        "Run the same command with '-ls, --list --screen' option added to see all operations of a Resource."
    )
    console.print()
    selected_operation_name = Prompt.ask(
        "[green bold] Select which operation",
        choices=operation_names,
        default=operation_names[0],
        console=console,
    )

    operation_doc_panel = get_documentation_panel_for_operation(
        balcony_aws, service, resource_name, selected_operation_name
    )
    # with console.pager(styles=True):
    #     console.print(operation_doc_panel)
    console.print(operation_doc_panel)
    console.print()

    boto3_google_search_uri = generate_google_search_uri(
        ["terraform", "provider", "aws", service, resource_name]
    )
    terraform_aws_docs_google_search_uri = generate_google_search_uri(
        ["boto3", service, resource_name, selected_operation_name]
    )

    console.print(
        Padding(
            Panel(  # noqa
                textwrap.dedent(
                    f"""
                Google — boto3 docs: [bold cyan]{terraform_aws_docs_google_search_uri}[/]
                
                Google — Terraform docs: [bold cyan]{boto3_google_search_uri}[/]                     
                """,
                ),  # noqa
                title="[bold blue]Google Search Links",
            ),
            (0, 2),
        ),
    )
    console.print()

    # behave like balcony does, as it reads lists of pages, so has a list of (responses,)
    mock_output_data_list = [
        gen_mock_output_data_for_operation(
            balcony_aws, service, resource_name, selected_operation_name
        ),
        gen_mock_output_data_for_operation(
            balcony_aws, service, resource_name, selected_operation_name
        ),
        # gen_mock_output_data_for_operation(
        #     balcony_aws, service, resource_name, selected_operation_name
        # ),
    ]

    console.rule("[bold cyan underline]JMESPath Query")
    console.print()
    confirm_jmespath_selector = False
    jmespath_selector = None
    jmespath_filtered_data = None
    do_ask_for_jmespath_selector = True
    while do_ask_for_jmespath_selector:
        input_jmespath_selector = Prompt.ask(
            "[green bold] Enter a jmespath query to filter the mock output data",
            console=console,
        )

        if not input_jmespath_selector:
            console.print("[red bold]You must enter a jmespath query.[/red bold]")
            continue

        try:
            _filtered_data = jmespath.search(
                input_jmespath_selector, mock_output_data_list
            )
        except jmespath.exceptions.ParseError as e:
            _filtered_data = False

        if not _filtered_data:
            console.print(
                f"[red bold]No data found for jmespath query {input_jmespath_selector}. Try again.[/red bold]"
            )
            continue  # loop again

        def _easy_on_the_eyes_dict(list_of_dicts):
            for _dict in list_of_dicts:
                if isinstance(_dict, dict):
                    for key, value in _dict.items():
                        if isinstance(value, dict):
                            _dict[key] = "{...omitted...}"
                        elif isinstance(value, list):
                            _dict[key] = "[...omitted...]"
            return list_of_dicts

        console.print_json(data=_easy_on_the_eyes_dict(_filtered_data), default=str)

        confirm_jmespath_selector = Confirm.ask(
            f"[yellow bold]Does the above data look correct? Are you sure to use [bold blue]{input_jmespath_selector}[/] jmespath query?[/]",
            console=console,
        )

        # check for confirmation and existence of actually filtered data
        if confirm_jmespath_selector and _filtered_data:
            jmespath_selector = input_jmespath_selector
            jmespath_filtered_data = _filtered_data
            # break out of the loop
            do_ask_for_jmespath_selector = False

            filtered_data_type_is_dict = isinstance(jmespath_filtered_data[0], dict)
            if not filtered_data_type_is_dict:
                # warn about the usage
                console.print(
                    Padding(
                        Panel(
                            f"[blue bold] Note:[/][blue] You've selected a non-dict data. You can access the elements with 'item' keyword.",
                            expand=False
                        ),
                        (1, 1),
                    )
                )
            continue

    # randomize the data ids, etc
    for filtered_mock_data in jmespath_filtered_data:
        random_string = "".join(random.choices(string.ascii_letters, k=4))
        if isinstance(filtered_mock_data, dict):
            for key, value in filtered_mock_data.items():
                if isinstance(value, str):
                    filtered_mock_data[key] = f"{value}-{random_string}"
        if isinstance(filtered_mock_data, list):
            filtered_mock_data = [
                f"{_m_data}-{random_string}" if isinstance(_m_data, str) else _m_data
                for _m_data in filtered_mock_data
            ]
        if isinstance(filtered_mock_data, str):
            filtered_mock_data = f"{filtered_mock_data}-{random_string}"
    console.print()
    console.rule("[cyan underline]Jinja2 Template for [bold]Terraform to Resource Name")
    console.print()
    console.print(
        "[yellow bold] The j2 template you provide must select unique values, or terraform will fail.[/]"
    )
    console.print(
        "You can directly access the attrs. by their name (e.g. PolicyId, RoleArn, ClusterName etc.)"
    )
    console.print(
        "You can also access the resource tags by their key prefixed with `tag_` (e.g. `tag_Name`, `tag_Environment` etc.)"
    )
    console.print(
        "Use `or` keyword to select the first non-empty value (e.g. `tag_Name or tag_Billing or InstanceId or PolicyId`)"
    )
    console.print()

    do_ask_for_j2_tpl_resource_name = True
    while do_ask_for_j2_tpl_resource_name:
        input_j2_tpl_resource_name = Prompt.ask(
            "[green bold] Enter a jinja2 template to generate the to_resource_name. Your input will be wrapped with '{{ }}'",
            console=console,
        )
        # wrap the input with {{ }}
        j2_tpl_resource_name = f"{{{{ {input_j2_tpl_resource_name} }}}}"

        # render the jinja2 template with the filtered data
        to_resource_name_list = []
        for filtered_datum in jmespath_filtered_data:
            _rendered_data_list = render_jinja2_template_with_data(
                filtered_datum, j2_tpl_resource_name
            )
            to_resource_name_list.extend(_rendered_data_list)

        console.print(
            Panel(
                Pretty(to_resource_name_list),
                title=f"Rendered your j2 template: {j2_tpl_resource_name}",
            )
        )
        console.print()
        confirm_j2_tpl_resource_name = Confirm.ask(
            f"[yellow bold]Are you sure to use [bold blue]{j2_tpl_resource_name}[/] ?[/]",
            console=console,
        )

        if confirm_j2_tpl_resource_name and to_resource_name_list:
            do_ask_for_j2_tpl_resource_name = False
            continue

    console.print()
    console.rule("[cyan underline]Jinja2 Template for [bold]Import ID")
    console.print()

    do_ask_for_j2_tpl_import_id = True
    while do_ask_for_j2_tpl_import_id:
        input_j2_tpl_import_id = Prompt.ask(
            "[green bold] Enter a jinja2 template to generate the Import ID. Your input will be wrapped with '{{ }}'",
            console=console,
        )
        # wrap the input with {{ }}
        j2_tpl_import_id = f"{{{{ {input_j2_tpl_import_id} }}}}"

        # render the jinja2 template with the filtered data
        import_id_list = []
        for filtered_datum in jmespath_filtered_data:
            _rendered_data_list = render_jinja2_template_with_data(
                filtered_datum, j2_tpl_import_id
            )
            import_id_list.extend(_rendered_data_list)

        console.print(
            Panel(
                Pretty(import_id_list),
                title=f"Rendered your j2 template: {j2_tpl_import_id}",
            )
        )
        console.print()
        confirm_j2_tpl_import_id = Confirm.ask(
            f"[yellow bold]Are you sure to use [bold blue]{j2_tpl_import_id}[/] ?[/]",
            console=console,
        )

        if confirm_j2_tpl_import_id and import_id_list:
            do_ask_for_j2_tpl_import_id = False
            continue

    console.print()
    console.rule("[bold cyan underline]Terraform Resource Type")
    console.print()

    do_ask_for_tf_resource_type = True
    while do_ask_for_tf_resource_type:
        to_terraform_resource_type = Prompt.ask(
            "[green bold]Enter Terraform Resource Type (e.g. aws_instance)",
            default=False,
            console=console,
        )

        confirm_tf_resource_type = Confirm.ask(
            f"[yellow bold]Are you sure to use [bold blue]{to_terraform_resource_type}[/] ?[/]",
            console=console,
        )
        if confirm_tf_resource_type:
            do_ask_for_tf_resource_type = False
            continue

    console.print()
    console.rule("")
    console.print()

    user_def_import_configurations = [
        {
            "service": service,
            "resource_node": resource_name,
            "operation_name": selected_operation_name,
            "jmespath_query": jmespath_selector,
            "to_resource_type": to_terraform_resource_type,
            "to_resource_name_jinja2_template": j2_tpl_resource_name,
            "id_generator_jinja2_template": j2_tpl_import_id,
        }
    ]

    yaml_output = gen_balcony_tf_import_config_yaml(user_def_import_configurations)
    # check yaml output validity

    if not yaml_output:
        console.print(
            f"[red bold]Error while generating yaml output. Enable --debug to see more messages.[/red bold]"
        )
        return False

    console.print("Your import-configuration yaml output:")
    console.print()
    console.print(
        Syntax(yaml_output, "yaml", theme="monokai", line_numbers=False)
    )  # noqa

    gen_filename = f"{service}-{resource_name}-wizard.yaml"
    saved_filepath = save_tf_input_config_to_user_defined_yaml_dir(
        gen_filename, yaml_output
    )

    if not saved_filepath:
        console.print(
            f"[yellow bold]Warning:[/] You can set a custom directory for your import configurations with [bold]BALCONY_TERRAFOM_IMPORT_CONFIG_DIR[/] environment variable."
        )
        console.print(
            f"If you set this, balcony will read your import configurations from that directory. And terraform-wizard will auto-save your generated import configuration to that directory."
        )
        console.print(
            Syntax(
                f"export BALCONY_TERRAFOM_IMPORT_CONFIG_DIR=~/balcony-tf-import-configs",
                "bash",
                theme="monokai",
                line_numbers=False,
            )
        )

    elif saved_filepath:
        console.print(
            f"[bold]Since you've set the env. var. 'BALCONY_TERRAFOM_IMPORT_CONFIG_DIR', auto save is enabled.[/]"
        )

        console.print(
            f"[green bold]SUCCESS: Your import-configuration yaml output saved to {saved_filepath}[/]"
        )

    return True
