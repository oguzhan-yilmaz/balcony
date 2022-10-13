from typing import Optional
import typer
try:
    from .utils import *
    from .logs import get_logger, get_rich_console, set_log_level_at_runtime
    from .nodes import ServiceNode
    from .reader import ServiceReader
    from .custom_nodes import *
    from .registries import app_registry
    from .factories import Boto3SessionSingleton, BalconyAWS
    from .settings import INSTALLED_BALCONY_APPS
except ImportError:
    from utils import *
    from logs import get_logger, get_rich_console, set_log_level_at_runtime
    from nodes import ServiceNode
    from reader import ServiceReader
    from custom_nodes import *
    from factories import Boto3SessionSingleton, BalconyAWS
    from registries import app_registry
    from settings import INSTALLED_BALCONY_APPS

# TODO allow single parameter selection with optional arg
from rich.json import JSON
import boto3
from rich.columns import Columns
from rich.panel import Panel
from rich.console import Console
from rich.layout import Layout
from rich.pretty import Pretty
import os
import logging

console = get_rich_console()
err_console = Console(stderr=True)
logger = get_logger(__name__)
session = Boto3SessionSingleton().get_session()
balcony_aws = BalconyAWS(session)
app = typer.Typer(no_args_is_help=True)
# aws_app = typer.Typer() # no_args_is_help=True
awsx_app = typer.Typer(no_args_is_help=True) # no_args_is_help=True
# app.add_typer(aws_app, name="aws")
app.add_typer(awsx_app, name="apps")
app_registry.import_balcony_apps(INSTALLED_BALCONY_APPS)


app_objects = []
registered_apps = app_registry.get_registered_apps()
for author, app_dict_list in registered_apps.items():
    for app_dict in app_dict_list:
        app_cls = app_dict.get('cls')
        app_name = app_dict.get('app_name')
        app_obj = app_cls()
        app_objects.append(app_obj)

        try:
            _typer_app = app_obj.get_cli_app()
            if _typer_app:
                awsx_app.add_typer(_typer_app, name=app_name)
        except NotImplementedError:
            print(app_name, 'has not implemented get_cli_app()') 
            

def _get_available_service_node_names():
    return get_all_available_services(session)

def generate_service_node_completion_items():
    service_names = _get_available_service_node_names(session)
    return service_names

def _complete_service_name(incomplete: str):
    service_names = _get_available_service_node_names()
    if not incomplete:
        for name in service_names:
            yield name
    else:
        for name in service_names:
            if name.startswith(incomplete):
                yield name
                
                
def _complete_resource_node_name(ctx: typer.Context, incomplete: str):
    service = ctx.params.get("service", False)
    if not service:
        return []
    service_node = balcony_aws.get_service(service)
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


        
        
# @aws_app.command('ls')
def _list_service_or_resource(
        service: Optional[str] = typer.Argument(None, show_default=False,help='The AWS service name', autocompletion=_complete_service_name),
        resource_node: Optional[str] = typer.Argument(None, show_default=False, help='The AWS Resource Node', autocompletion=_complete_resource_node_name),
    ):

    available_service_names = _get_available_service_node_names()
    if not service and not resource_node:
        # nothing is given
        console.print(Columns(available_service_names, equal=True, expand=True))
        return
    
    if service and not resource_node:
        # we only have service name
        
        if service not in available_service_names:
            similar_service_names = ifind_similar_names_in_list(service, available_service_names)
            if similar_service_names:
                console.print(f"[yellow]Found Similar Service Names:")
                console.print(Columns(similar_service_names, equal=True, expand=True))
                return
            else:
                raise typer.Exit(f"Invalid service name: {service}. Please pick a proper one.")
            
        service_node = balcony_aws.get_service(service)
        resource_nodes = service_node.get_resource_nodes()
        
        resource_node_names = []
        for _rn in resource_nodes:
            _rn_name = _rn.name
            if _rn.get_all_required_parameter_names():
                _rn_name = f"[bold]{_rn_name}[/]"
            resource_node_names.append(_rn_name)
        
        resource_node_name_as_columns =  Columns(resource_node_names, equal=True, expand=True)
        console.print(resource_node_name_as_columns)
        return
        
    elif service and resource_node:
        # we got both options filled
        service_node = balcony_aws.get_service(service) 
        resource_nodes = service_node.get_resource_nodes()
        resource_node_names = [ _rn.name for _rn in resource_nodes]
        resource_node_obj = service_node.get_resource_node_by_name(resource_node)
        if not resource_node_obj:
            
            similar_resource_names = ifind_similar_names_in_list(resource_node, resource_node_names)
            if similar_resource_names:
                console.print(f"[yellow]Found Similar Resource Node Names:")
                console.print(Columns(similar_resource_names, equal=True, expand=True))
                return 
            else:
                raise typer.Exit(f"Invalid Resource Node name: [bold]{resource_node}[/] for Service: [bold]{service}[/].")
        operations_panel = service_node._get_operation_details_panel(resource_node_obj.name)
        console.print(operations_panel)
        return    


@app.command('aws')
def _cli_aws_command(
        service: Optional[str] = typer.Argument(None, show_default=False,help='The AWS service name', autocompletion=_complete_service_name),
        resource_node: Optional[str] = typer.Argument(None, show_default=False, help='The AWS Resource Node', autocompletion=_complete_resource_node_name),
        list_contents: bool = typer.Option(False, "--list", '-l'),
        debug: bool = typer.Option(False, "--debug", '-d'),
        paginate: bool = typer.Option(False, "--paginate", '-p'),
    ):
    if debug:
        set_log_level_at_runtime(logging.DEBUG)
    
    if list_contents:
        _list_service_or_resource(service, resource_node)
        return

    available_service_names = _get_available_service_node_names()
    if not service and not resource_node:
        _list_service_or_resource(service, resource_node)
        console.print(Panel(f"[bold]Please pick one of the AWS Services", title="[red][bold]ERROR"))
        return
    if service and not resource_node:
        _list_service_or_resource(service, resource_node)
        console.print(Panel(f"[bold]Please pick one of the Resource Nodes from [green]{service}[/] Service", title="[red][bold]ERROR"))
        return
    elif service and resource_node:
        service_node = balcony_aws.get_service(service)
        service_reader = service_node.get_service_reader()
        read = service_reader.read_resource_node(resource_node)
        if paginate:
            with console.pager(styles=True):
              console.print_json(data=read, default=str)
        else:    
            console.print_json(data=read, default=str)
        return
    
    
def run_app():
    app(prog_name="balcony")
    
if __name__ == "__main__":
    run_app()
    




