import typer
try:
    from .utils import *
    from .logs import get_logger, get_rich_console, set_log_level_at_runtime
    from .nodes import ServiceNode, OperationType
    from .reader import ServiceReader
    from .custom_nodes import *
    from .registries import app_registry
    from .factories import Boto3SessionSingleton, BalconyAWS
    from .settings import INSTALLED_BALCONY_APPS
except ImportError:
    from utils import *
    from logs import get_logger, get_rich_console, set_log_level_at_runtime
    from nodes import ServiceNode, OperationType
    from reader import ServiceReader
    from custom_nodes import *
    from factories import Boto3SessionSingleton, BalconyAWS
    from registries import app_registry
    from settings import INSTALLED_BALCONY_APPS

from typing import Optional
import boto3
from rich.columns import Columns
from rich.panel import Panel
from rich.console import Console
from rich.layout import Layout
from rich.pretty import Pretty
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

def _complete_operation_type(ctx: typer.Context, incomplete: str):
    service = ctx.params.get("service", False)
    resource_node = ctx.params.get("resource_node", False)
    if not service or not resource_node:
        return []
    service_node = balcony_aws.get_service(service)
    if not service_node:
        return []
    resource_node_obj = service_node.get_resource_node_by_name(resource_node)
    if not resource_node_obj:
        return []
    
    operation_types_and_names = resource_node_obj.get_operation_types_and_names()
    
    return list(operation_types_and_names.keys())
        
        
# @aws_app.command('ls')
def _list_service_or_resource(
        service: Optional[str] = typer.Argument(None, show_default=False,help='The AWS service name', autocompletion=_complete_service_name),
        resource_node: Optional[str] = typer.Argument(None, show_default=False, help='The AWS Resource Node', autocompletion=_complete_resource_node_name),
    ):

    available_service_names = _get_available_service_node_names()
    if not service and not resource_node:
        # nothing is given
        console.print(Columns(available_service_names, equal=True, expand=True))
        return available_service_names
    
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
        return resource_node_names
        
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

def aa():
    # for sname in balcony_aws.get_available_service_node_names():
    service_node = balcony_aws.get_service('iam')
    for rn in service_node.get_resource_nodes():
        for operation in rn.get_operation_names():
            print(operation)
    
@app.command('aws')
def aws_main_command(
        service: Optional[str] = typer.Argument(None, show_default=False,help='Name of the AWS Service', autocompletion=_complete_service_name),
        resource_node: Optional[str] = typer.Argument(None, show_default=False, help='Name of the AWS Resource Node', autocompletion=_complete_resource_node_name),
        operation: Optional[OperationType] = typer.Option(None, "--operation", '-o', show_default=False, help='Select a specific operation type.', ),
        patterns: Optional[List[str]] = typer.Option(None, "--pattern", '-p', show_default=False, help='UNIX pattern matching for generated parameters. Should be quoted. e.g. (-p "*prod-*")', auto_complete=_complete_operation_type),
        list_contents: bool = typer.Option(False, "--list", '-l', help='Print the details of Service or Resource. Does not make requests.'),
        debug: bool = typer.Option(False, "--debug", '-d', help='Enable debug messages.'),
        paginate: bool = typer.Option(False, "--screen", '-s', help='Open the data on a separate paginator on shell.'),
    ):
    if debug:
        set_log_level_at_runtime(logging.DEBUG)
    
    if list_contents:
        _list_service_or_resource(service, resource_node)
        return

    # available_service_names = _get_available_service_node_names()
    if not service and not resource_node:
        available_services = _list_service_or_resource(service, resource_node)
        console.print(Panel(f"[bold]Please pick one of the AWS Services", title="[red][bold]ERROR"))
        return {'services':available_services}
    
    if service and not resource_node:
        available_resources = _list_service_or_resource(service, resource_node)
        console.print(Panel(f"[bold]Please pick one of the Resource Nodes from [green]{service}[/] Service", title="[red][bold]ERROR"))
        return {'service':service, 'resources': available_resources}
    elif service and resource_node:
        service_node = balcony_aws.get_service(service)
        service_reader = service_node.get_service_reader()
        
        is_operation_selected = operation is not None
        read_data = None
        if not is_operation_selected:
            read_data = service_reader.read_resource_node(resource_node, match_patterns=patterns)
          
        else: # Operation is selected
            
            resource_node_obj = service_node.get_resource_node_by_name(resource_node)
            types_to_op_names = resource_node_obj.get_operation_types_and_names()
            supported_operation_types = list(types_to_op_names.keys())
            operation_name = types_to_op_names.get(operation.value, False)
            if not operation_name:
                console.print(f"[red bold]Given {operation.value} is not supported by {resource_node}. Try: {supported_operation_types}")
                return False
            console.print(patterns)
            read_data = service_reader.read_operation(resource_node, operation_name, match_patterns=patterns)

        if paginate:
            with console.pager(styles=True):
                console.print_json(data=read_data, default=str)
        else:    
            console.print_json(data=read_data, default=str)
        return read_data

    
def run_app():
    app(prog_name="balcony")
    

    
if __name__ == "__main__":
    run_app()
    