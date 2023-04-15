import json
from utils import get_all_available_services, ifind_similar_names_in_list
from config import (
    get_logger,
    get_rich_console,
    set_log_level_at_runtime,
    clear_relations_cache,
)
from custom_nodes import *  # noqa
from aws import BalconyAWS

import typer
import jmespath
from typing import Optional, List, Dict
from rich.columns import Columns
from rich.panel import Panel
import logging
import boto3
from pathlib import Path


console = get_rich_console()
logger = get_logger(__name__)
session = boto3.session.Session()
service_factory = BalconyAWS(session)
app = typer.Typer(no_args_is_help=True)


@app.callback()
def _main_app_callback(
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug messages."),
):
    if debug:
        set_log_level_at_runtime(logging.DEBUG)


def _get_available_service_node_names():
    return get_all_available_services(session)


def generate_service_node_completion_items():
    service_names = _get_available_service_node_names(session)
    return service_names


def save_dict_to_output_file(output_filepath: str, data: Dict):
    with open(output_filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)


def save_str_list_to_output_file(output_filepath: str, lines: List[str]):
    with open(output_filepath, "w") as f:
        f.writelines([line + "\n" for line in lines])


def _complete_service_name(incomplete: str):
    service_names = _get_available_service_node_names()
    if not incomplete:
        for name in service_names:
            yield name
    else:
        for name in service_names:
            if name.startswith(incomplete):
                yield name


def _complete_resource_node_name(ctx: typer.Context, incomplete: str) -> List[str]:
    service = ctx.params.get("service", False)
    if not service:
        return []
    service_node = service_factory.get_service_node(service)
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
    service_node = service_factory.get_service_node(service)
    if not service_node:
        return []
    resource_node_obj = service_node.get_resource_node_by_name(resource_node)
    if not resource_node_obj:
        return []
    operation_types_and_names = resource_node_obj.get_operation_types_and_names()
    return list(operation_types_and_names.keys())


def _list_service_or_resource(
    service: Optional[str] = typer.Argument(
        None,
        show_default=False,
        help="The AWS service name",
        autocompletion=_complete_service_name,
    ),
    resource_node: Optional[str] = typer.Argument(
        None,
        show_default=False,
        help="The AWS Resource Node",
        autocompletion=_complete_resource_node_name,
    ),
    screen_pager: Optional[bool] = typer.Option(
        False,
        help="Use a new screen to show the output",
    )
) -> None:

    available_service_names = _get_available_service_node_names()
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

        service_node = service_factory.get_service_node(service)
        resource_nodes = service_node.get_resource_nodes()

        resource_node_names = []
        for _rn in resource_nodes:
            _rn_name = _rn.name
            if len(_rn.get_all_required_parameter_names()) >= 2:
                _rn_name = f"[bold red]{_rn_name}[/]"
            elif len(_rn.get_all_required_parameter_names()) >= 1:
                _rn_name = f"[bold green]{_rn_name}[/]"
            resource_node_names.append(_rn_name)

        resource_node_name_as_columns = Columns(
            resource_node_names, equal=True, expand=True
        )
        console.print(resource_node_name_as_columns)
        return resource_node_names

    elif service and resource_node:
        # we got both options filled
        service_node = service_factory.get_service_node(service)
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
        return


@app.command("aws", help="List AWS services, Call read-operations, Show documentation")
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
        help="Python f-string expression to generate a line for each item.",
    ),
    list_contents: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="Print the details of Service or Resource. Does not make requests.",
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
        help="Output JSON file name. If not provided, will print to console.",
    )
): 
    if not follow_pagination:
        logger.warning("[yellow bold][WARNING][/] [bold]--paginate, -p[/] option is NOT set. You're likely to get incomplete data.")
    if debug:
        set_log_level_at_runtime(logging.DEBUG)
    if list_contents:
        _list_service_or_resource(service, resource_node, screen_pager=screen)
        return

    if not service and not resource_node:
        available_services = _list_service_or_resource(service, resource_node)
        console.print(
            Panel("[bold]Please pick one of the AWS Services", title="[red][bold]ERROR")
        )
        return {"services": available_services}

    if service and not resource_node:
        available_resources = _list_service_or_resource(service, resource_node)
        console.print(
            Panel(
                f"[bold]Please pick one of the Resource Nodes from [green]{service}[/] Service",
                title="[red][bold]ERROR",
            )
        )
        return {"service": service, "resources": available_resources}

    elif service and resource_node:
        service_node = service_factory.get_service_node(service)
        service_reader = service_node.get_service_reader()

        is_operation_selected = operation is not None
        read_data = None
        if not is_operation_selected:
            # read all operations in given resource node
            read_data = service_reader.read_resource_node(
                resource_node, match_patterns=patterns, follow_pagination=follow_pagination
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
                return False
            read_data = service_reader.read_operation(
                resource_node, operation_name, match_patterns=patterns, refresh=False, follow_pagination=follow_pagination
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
                        logger.debug(f"Failed to format  [red]{str(e)}[/] with data: {r_data}")

                if output_file:
                    output_filepath = Path(output_file).resolve()
                    logger.info(f"Saving output to: {output_filepath}")
                    save_str_list_to_output_file(output_filepath, formatted_output_list)
                    return
                else:
                    # print to console
                    console.print('\n'.join(formatted_output_list), overflow="ignore")
                    return read_data
            else:
                logger.debug(f"[red]No data found.[/] Failed to use --format: '{formatter}'")

        if screen:
            with console.pager(styles=True):
                console.print_json(data=read_data, default=str)
        elif output_file:
            output_filepath = Path(output_file).resolve()
            logger.info(f"Saving output to: {output_filepath}")
            save_dict_to_output_file(output_filepath, read_data)
        else:
            console.print_json(data=read_data, default=str)
        return read_data


@app.command("clear-cache", help="Clear relations json cache")
def clear_cache_command(
    # service: Optional[str] = typer.Argument(None, show_default='all',
    # help='Name of the Service to clear relation caches of', autocompletion=_complete_service_name),
):
    logger.debug("Deleting relations cache for services:")
    deleted_service_caches = clear_relations_cache()
    for deleted_service in deleted_service_caches:
        logger.info(f"[green]Deleted[/] {deleted_service}")

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
