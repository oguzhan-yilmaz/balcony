import json
import textwrap
from utils import (
    get_all_available_services,
    ifind_similar_names_in_list,
    _create_boto_session,
    is_terraform_aws_resource_type
)
from config import (
    get_logger,
    get_rich_console,
    set_log_level_at_runtime,
    clear_relations_cache,
    BALCONY_RELATIONS_DIR
)

# required for loading custom resource nodes into registry
from custom_nodes import *  # noqa
from aws import BalconyAWS
from rich.text import Text
import typer
import jmespath
from typing import Optional, List, Dict, Generator
from rich.columns import Columns
from rich.panel import Panel
import logging
from pathlib import Path
from terraform_import.importer import (
    generate_import_block_for_resource,
    get_importable_resources,
)
from terraform_import.wizard import (
    interactive_help,
)
from rich.padding import Padding
import re

console = get_rich_console()
logger = get_logger(__name__)
session = _create_boto_session()
balcony_aws = BalconyAWS(session)
app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)



@app.callback()
def _main_app_callback(
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug messages."),
):
    if debug:
        set_log_level_at_runtime(logging.DEBUG)


def save_dict_to_output_file(output_filepath: str, data: Dict):
    with open(output_filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)


def save_str_list_to_output_file(output_filepath: str, lines: List[str]):
    with open(output_filepath, "w") as f:
        if lines:
            f.writelines([str(line) + "\n" for line in lines])


def _complete_service_name(incomplete: str) -> Generator[str, None, None]:
    """Typer autocompletion function. Finds matching service names.

    Args:
        incomplete (str): Service names that're starting with this string.

    Yields:
        _type_: _description_
    """
    service_names = get_all_available_services(session)
    if not incomplete:
        for name in service_names:
            yield name
    else:
        for name in service_names:
            if name.startswith(incomplete):
                yield name


def _complete_resource_node_name(
    ctx: typer.Context, incomplete: str
) -> Generator[str, None, None]:
    service = ctx.params.get("service", False)
    if not service:
        return []
    service_node = balcony_aws.get_service_node(service)
    if not service_node:
        return []
    resource_nodes = service_node.get_resource_nodes()
    if not resource_nodes:
        return []

    resource_node_names = []

    for _rn in resource_nodes:
        _rn_name = _rn.name
        if incomplete:
            if _rn_name.lower().startswith(incomplete.lower()):
                resource_node_names.append(_rn_name)
        else:
            resource_node_names.append(_rn_name)
    return resource_node_names


def _complete_operation_type(ctx: typer.Context) -> List[str]:
    service = ctx.params.get("service", False)
    resource_node = ctx.params.get("resource_node", False)
    if not service or not resource_node:
        return []
    service_node = balcony_aws.get_service_node(service)
    if not service_node:
        return []
    resource_node_obj = service_node.get_resource_node_by_name(resource_node)
    if not resource_node_obj:
        return []
    operation_types_and_names = resource_node_obj.get_operation_types_and_names()
    return list(operation_types_and_names.keys())


def _list_service_or_resource(
    service: Optional[str] = False,
    resource_node: Optional[str] = False,
    screen_pager: Optional[bool] = False,
) -> None:

    available_service_names = get_all_available_services(session)
    if not service and not resource_node:
        # nothing is given
        console.print(Columns(available_service_names, equal=True, expand=True))
        return available_service_names

    if service and not resource_node:
        # we only have service name

        if service not in available_service_names:
            similar_service_names = ifind_similar_names_in_list(
                service, available_service_names
            )
            if similar_service_names:
                console.print("[yellow]Found Similar Service Names:")
                console.print(Columns(similar_service_names, equal=True, expand=True))
                return
            else:
                raise typer.Exit(
                    f"Invalid service name: {service}. Please pick a proper one."
                )

        service_node = balcony_aws.get_service_node(service)
        resource_nodes = service_node.get_resource_nodes()

        resource_node_names = []
        for _rn in resource_nodes:
            _rn_name = _rn.name
            # if len(_rn.get_all_required_parameter_names()) >= 2:
            #     _rn_name = f"[bold red]{_rn_name}[/]"
            # elif len(_rn.get_all_required_parameter_names()) >= 1:
            #     _rn_name = f"[bold green]{_rn_name}[/]"
            resource_node_names.append(_rn_name)

        resource_node_name_as_columns = Columns(
            resource_node_names, equal=True, expand=True
        )
        console.print(resource_node_name_as_columns)
        return resource_node_names

    elif service and resource_node:
        # we got both options filled
        service_node = balcony_aws.get_service_node(service)
        resource_nodes = service_node.get_resource_nodes()
        resource_node_names = [_rn.name for _rn in resource_nodes]
        resource_node_obj = service_node.get_resource_node_by_name(resource_node)
        if not resource_node_obj:

            similar_resource_names = ifind_similar_names_in_list(
                resource_node, resource_node_names
            )
            if similar_resource_names:
                console.print("[yellow]Found Similar Resource Node Names:")
                console.print(Columns(similar_resource_names, equal=True, expand=True))
                return
            else:
                raise typer.Exit(
                    f"Invalid Resource Node name: [bold]{resource_node}[/] for Service: [bold]{service}[/]."
                )
        operations_panel = service_node._get_operation_details_panel(
            resource_node_obj.name
        )
        if screen_pager:
            with console.pager(styles=True):
                console.print(operations_panel)
        else:
            console.print(operations_panel)
        return


@app.command(
    "aws",
    help="Read your AWS Resource Nodes as JSON. Use --debug option if you're stuck!",
)
def aws_main_command(  # noqa
    service: Optional[str] = typer.Argument(
        None,
        show_default=False,
        help="Name of the AWS Service",
        autocompletion=_complete_service_name,
    ),
    resource_node: Optional[str] = typer.Argument(
        None,
        show_default=False,
        help="Name of the AWS Resource Node",
        autocompletion=_complete_resource_node_name,
    ),
    operation: Optional[str] = typer.Argument(
        None,
        show_default=False,
        help="Select a specific operation type. <get, gets, list, describe>",
        autocompletion=_complete_operation_type,
    ),
    patterns: Optional[List[str]] = typer.Option(
        None,
        "--pattern",
        show_default=False,
        help='UNIX pattern matching for generated parameters. Should be quoted. e.g. (--pattern "*prod-*")',
    ),
    jmespath_selector: Optional[str] = typer.Option(
        None,
        "--jmespath-selector",
        "-js",
        show_default=False,
        help="JMESPath query selector to filter resulted data. Visit for tutorial: https://jmespath.org/tutorial.html",
    ),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug messages."),
    formatter: Optional[str] = typer.Option(
        None,
        "--format",
        "-f",
        show_default=False,
        help="Python f-string expression to generate a string for each item.",
    ),
    list_contents: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="Print the documentation of Service or Resource. Does not make requests.",
    ),
    screen: bool = typer.Option(
        False, "--screen", "-s", help="Open the data on a separate paginator on shell."
    ),
    follow_pagination: bool = typer.Option(
        False,
        "--paginate",
        "-p",
        help="Paginate through the output if the output is truncated, otherwise will only read one page.",
    ),
    output_file: str = typer.Option(
        None,
        "--output",
        "-o",
        show_default=False,
        help="Output JSON file name. If not provided, will print to console.",
    ),
):
    if debug:
        set_log_level_at_runtime(logging.DEBUG)

    if list_contents:
        _list_service_or_resource(service, resource_node, screen_pager=screen)
        raise typer.Exit()

    # warn user if pagination is not set
    if not follow_pagination:
        logger.debug(
            "[underline][yellow bold][WARNING][/] [bold][--paginate, -p][/] option [bold red]is NOT set[/]. You're likely to get incomplete data.[/]"
        )
    service_markup = f"[green]{service}[/]"

    if not service and not resource_node:
        # print out resource nodes of this service.
        _list_service_or_resource(service, resource_node, screen_pager=screen)
        console.print(
            Panel("[bold]Please pick one of the AWS Services", title="[red][bold]ERROR")
        )
        raise typer.Exit()

    if service and not resource_node:
        _list_service_or_resource(service, resource_node, screen_pager=screen)
        console.print(
            Panel(
                f"[bold]Please pick one of the Resource Nodes from {service_markup} Service",
                title="[red][bold]ERROR",
            )
        )
        raise typer.Exit()

    elif service and resource_node:
        service_node = balcony_aws.get_service_node(service)
        service_reader = service_node.get_service_reader()

        is_operation_selected = operation is not None
        read_data = None
        if not is_operation_selected:
            # read all operations in given resource node
            read_data = service_reader.read_resource_node(
                resource_node,
                match_patterns=patterns,
                follow_pagination=follow_pagination,
            )

        else:  # Operation is selected
            resource_node_obj = service_node.get_resource_node_by_name(resource_node)
            types_to_op_names = resource_node_obj.get_operation_types_and_names()
            supported_operation_types = list(types_to_op_names.keys())
            operation_name = types_to_op_names.get(operation, False)
            if not operation_name:
                console.print(
                    f"[red bold]Given {operation} is not supported by {resource_node}. Try: {supported_operation_types}"
                )
                raise typer.Exit(code=-1)

            read_data = service_reader.read_operation(
                resource_node,
                operation_name,
                match_patterns=patterns,
                refresh=False,
                follow_pagination=follow_pagination,
            )

        if jmespath_selector:

            logger.debug(
                f"Using jmespath selector: {jmespath_selector} to query the returned data."
            )
            read_data = jmespath.search(jmespath_selector, read_data)

        if formatter:
            if read_data:
                formatted_output_list = []
                for r_data in read_data:
                    try:
                        # try to format and add it to output lines list
                        formatted_output_list.append(formatter.format(**r_data))
                    except AttributeError as e:
                        logger.debug(
                            f"Failed to format  [red]{str(e)}[/] with data: {r_data}"
                        )

                if output_file:
                    output_filepath = Path(output_file).resolve()
                    logger.info(f"Saving output to: {output_filepath}")
                    save_str_list_to_output_file(output_filepath, formatted_output_list)
                    raise typer.Exit()
                else:
                    # print to console
                    console.print("\n".join(formatted_output_list), overflow="ignore")
                    raise typer.Exit()
            else:
                logger.debug(
                    f"[red]No data found.[/] Failed to use --format: '{formatter}'"
                )

        if screen:
            with console.pager(styles=True):
                console.print_json(data=read_data, default=str)
        elif output_file:
            output_filepath = Path(output_file).resolve()
            logger.info(f"Saving output to: {output_filepath}")
            save_dict_to_output_file(output_filepath, read_data)
        else:
            console.print_json(data=read_data, default=str)
        raise typer.Exit()


@app.command(
    "terraform-import-support-matrix",
    # no_args_is_help=True,
    short_help="Show Terraform Import Support Matrix for AWS Services.",
    help="""Show Terraform Import Support Matrix for AWS Services.""",
)
def terraform_import_support_matrix(
    no_markdown_render: bool = typer.Option(
        False,
        "--no-md-render",
        help="Doesn't renders the markdown table, instead prints the raw data.",
    ),
):
    service_resource_list = get_importable_resources()

    header = f"# Balcony Terraform Import Support Matrix\n".format()
    header += f"| {'TerraformResourceType':<50} | {'Service':>15} | {'Resource':45} |\n".format()
    header += f"| {'---':50} | {'---':15} | {'---':45} |\n".format()
    result = header

    for i, (terraform_type, service_name, resource_name) in enumerate(
        service_resource_list
    ):
        cur_line = f"| {terraform_type:<50} | {service_name:>15} | {resource_name:45} |"
        result += cur_line + "\n"

    if no_markdown_render:
        console.print(result)
    else:
        from rich.markdown import Markdown
        console.print(Markdown(result))




@app.command(
    "terraform-import",
    no_args_is_help=True,
    short_help="Generate Terraform import blocks for a given AWS Service and Resource Node.",
    help="""
    Visit Balcony Terraform Import Documentation: https://oguzhan-yilmaz.github.io/balcony/terraform-import/ to learn more.\n
    """,
)
def terraform_import_command(
    service_or_tf_resource_type: Optional[str] = typer.Argument(
        None,
        show_default=False,
        help="Name of the AWS Service (ec2, iam) or Terraform Type (aws_iam_user)",
        autocompletion=_complete_service_name,
    ),
    resource_node: Optional[str] = typer.Argument(
        None,
        show_default=False,
        help="Name of the AWS Resource Node (Instances, Buckets, DBInstances)",
        autocompletion=_complete_resource_node_name,
    ),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug messages."),
    follow_pagination: bool = typer.Option(
        False,
        "--paginate",
        "-p",
        help="Paginate through the output if the output is truncated, otherwise will only read one page.",
    ),
    list_available_resources: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="Lists currently available resources for generating Terraform import blocks.",
    ),
    output_file: str = typer.Option(
        None,
        "--output",
        "-o",
        show_default=False,
        help="Output file name. If not provided, will print to console.",
    ),
    screen: bool = typer.Option(
        False, "--screen", "-s", help="Open the data on a separate paginator on shell."
    ),
):
    # set debug level if enabled
    if debug:
        set_log_level_at_runtime(logging.DEBUG)

    # warn user if pagination is not set
    if not follow_pagination:
        logger.debug(
            "[underline][yellow bold][WARNING][/] [bold][--paginate, -p][/] option [bold red]is NOT set[/]. You're likely to get incomplete data.[/]"
        )

    if list_available_resources:
        service_resource_list = get_importable_resources()

        def render_importable_resources(service_and_resource_tuples: List[Tuple]):
            header = f"[bold green]{'TerraformResourceType':<50} {'Service':>15} {'Resource':45}[/]\n".format()
            result = header

            for i, (terraform_type, service_name, resource_name) in enumerate(
                service_and_resource_tuples
            ):
                cur_line = f"{terraform_type:<50} {service_name:>15} {resource_name:45}"
                if i % 2:
                    cur_line = f"[bold]{cur_line}[/]"
                result += cur_line + "\n"
            return result

        rendered_service_resource_list = render_importable_resources(
            service_resource_list
        )
        console.print(rendered_service_resource_list)
        return  # list option is enabled, do not run the actual importing code.

    is_terraform_r_type_given = is_terraform_aws_resource_type(service_or_tf_resource_type) and resource_node is None
    if is_terraform_r_type_given:
        logger.debug(f"Terraform resource type is given: {service_or_tf_resource_type} instead of service and resource node.")
        pass
    elif (not service_or_tf_resource_type) or (not resource_node):
        _list_service_or_resource(service_or_tf_resource_type, resource_node, screen_pager=screen)
        console.print(f"[red bold]Please pick a Service and Resource Node[/]")
        return

    import_blocks = None
    if is_terraform_r_type_given:
        import_blocks = generate_import_block_for_resource(
            balcony_aws,
            terraform_resource_type=service_or_tf_resource_type,
            follow_pagination=follow_pagination
        )
    else:
        import_blocks = generate_import_block_for_resource(
            balcony_aws,
            service=service_or_tf_resource_type,
            resource_node=resource_node,
            follow_pagination=follow_pagination,
        )

    if not import_blocks:
        logger.debug(f"No import blocks generated for {service_or_tf_resource_type}.{resource_node}")

        fail_msg = textwrap.dedent(
            f"""
            No terraform import blocks generated for [bold]{service_or_tf_resource_type}.{resource_node}[/]. Some checks:
                
                - [underline]Run the balcony with [bold]--debug[/] flag to see more info.[/]
                    Run     [bold]balcony terraform-import --debug {service_or_tf_resource_type} {resource_node}[/]
                    
                - [underline]Do you have the correct AWS credentials and Region?[/]
                    Run     [bold]printenv | grep ^AWS_[/]
                
                - [underline]Is the resource node name correct?[/]
                    Run     [bold]balcony aws {service_or_tf_resource_type}[/]      to see available resource nodes.
                
                - [underline]You may not have any resources in your AWS Account, check it first:[/]
                    Run     [bold]balcony aws {service_or_tf_resource_type} {resource_node} -d[/] 
            """
        ).strip()
        console.print(Padding(fail_msg, (1, 1)))
        raise typer.Exit(-1)

    if output_file:
        output_filepath = Path(output_file).resolve()
        logger.info(f"Saving output to: {output_filepath}")
        save_str_list_to_output_file(output_filepath, import_blocks)
        raise typer.Exit()

    else:
        if screen:
            with console.pager(styles=True):
                console.print("\n".join(import_blocks))
        else:            
            console.print("\n".join(import_blocks))

    return  # import_blocks


@app.command(
    "terraform-wizard",
    no_args_is_help=True,
    short_help="Wizard that helps you to create the correct import-configuration interactively for the 'terraform-import' command.",
    help="""
    Visit Balcony Terraform Wizard Documentation: https://oguzhan-yilmaz.github.io/balcony/terraform-import-wizard/ to learn more.\n
    Hey, there! If you want to auto-save what you genereate, set the environment variable: BALCONY_TERRAFOM_IMPORT_CONFIG_DIR\n
    > $ export BALCONY_TERRAFOM_IMPORT_CONFIG_DIR=$HOME/balcony-tf-yamls\n
    And please create PRs and share your terraform import-configurations and help balcony to grow! Peace!\n
    """,
)
def wizard_the_terraform_import_configurer(
    service: Optional[str] = typer.Argument(
        None,
        show_default=False,
        help="Name of the AWS Service (e.g. ec2, s3, rds)",
        autocompletion=_complete_service_name,
    ),
    resource_node: Optional[str] = typer.Argument(
        None,
        show_default=False,
        help="Name of the AWS Resource Node. (e.g. Instances, Buckets, DBInstances)",
        autocompletion=_complete_resource_node_name,
    ),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug messages."),
    list_contents: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="Show documentation about the currently selected Service and ResourceNode. Does not make requests.",
    ),
    screen: bool = typer.Option(
        False, "--screen", "-s", help="Open the data on a separate paginator on shell."
    ),
):
    # set debug level if enabled
    if debug:
        set_log_level_at_runtime(logging.DEBUG)

    if list_contents:
        _list_service_or_resource(service, resource_node, screen_pager=screen)
        raise typer.Exit()

    if (not service) or (not resource_node):
        _list_service_or_resource(service, resource_node, screen_pager=screen)

        console.print(f"[red bold]Please pick a Service and Resource Node[/]")
        return

    # if we got here, we have both service and resource node
    interactive_help(balcony_aws, service, resource_node)
    return


@app.command("clear-cache", help=f"Clear relations json cache, located at: {BALCONY_RELATIONS_DIR}")
def clear_cache_command(
    # service: Optional[str] = typer.Argument(None, show_default='all',
    # help='Name of the Service to clear relation caches of', autocompletion=_complete_service_name),
):
    logger.debug("Deleting relations cache for services:")
    deleted_service_caches = clear_relations_cache()
    for deleted_service in deleted_service_caches:
        logger.info(f"[green]Deleted[/] {deleted_service}")


@app.command(
    "info",
    help="Information about the AWS Profile and Region currently used",
)
def info_command():
    created_session = balcony_aws.boto3_session
    console.print(
        f"[bold underline]AWS Region:[/] [bold blue]{created_session.region_name}[/]"
    )
    console.print(
        f"[bold underline]AWS Profile:[/] [bold blue]{created_session.profile_name}"
    )
    console.print()
    console.print("[bold underline]Available Profiles:[/]")

    for available_profile in created_session.available_profiles or []:
        console.print(f"  - [green bold]{available_profile}[/]")
    console.print(
        textwrap.dedent(
            """
        [yellow]You can configure the AWS Profile and Region by setting the
        the $[bold]AWS_DEFAULT_REGION[/] and $[bold]AWS_PROFILE[/] environment variables.[/]
    """
        )
    )


# @app.command('version', help='Show version info' )
# def version_command():
#     from importlib.metadata import version
#     console.print(__package__)
#     version=version(__package__)
#     console.print(version)


def run_app():
    app(prog_name="balcony")


if __name__ == "__main__":
    run_app()
