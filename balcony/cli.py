import typer
try:
    from .utils import *
    from .config import get_logger, get_rich_console, set_log_level_at_runtime
    from .nodes import ServiceNode, OperationType
    from .reader import ServiceReader
    from .custom_nodes import *
    from .factories import Boto3SessionSingleton, BalconyAWS
except ImportError:
    from utils import *
    from config import get_logger, get_rich_console, set_log_level_at_runtime
    from nodes import ServiceNode, OperationType
    from reader import ServiceReader
    from custom_nodes import *
    from factories import Boto3SessionSingleton, BalconyAWS

import jmespath
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

@app.callback()
def _main_app_callback(        
        debug: bool = typer.Option(False, "--debug", '-d', help='Enable debug messages.'),
    ):
    if debug:
        set_log_level_at_runtime(logging.DEBUG)
    
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

def _complete_operation_type(ctx: typer.Context):
    # service, resource_node = 'ec2', 'BundleTasks'
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

def vvv():
    service_node = balcony_aws.get_service('iam')
    rns = service_node.get_resource_nodes()
    
    a = []
    for k, v in service_node.client._PY_TO_OP_NAME.items():
        console.print(f"| {k} | {v} |")
    
def aa():
    s_count = 0
    total_rn_count = 0
    total_o_count = 0
    all_o_count = 0 
    for sname in balcony_aws.get_available_service_node_names():
        service_node = balcony_aws.get_service(sname)
        s_count += 1
        all_o_count += len(service_node.client._PY_TO_OP_NAME)
        rns = service_node.get_resource_nodes()
        rn_count = len(rns)
        total_rn_count += rn_count
        o_count = 0
        for rn in rns:
            o_count += len(rn.get_operation_names())
        console.print(sname, rn_count, o_count)

        total_o_count += o_count
    console.print(s_count, total_rn_count, total_o_count)    
    console.print(all_o_count)   
    
@app.command('aws')
def aws_main_command(
        service: Optional[str] = typer.Argument(None, show_default=False,help='Name of the AWS Service', autocompletion=_complete_service_name),
        resource_node: Optional[str] = typer.Argument(None, show_default=False, help='Name of the AWS Resource Node', autocompletion=_complete_resource_node_name),
        operation: Optional[str] = typer.Argument(None, show_default=False, help='Select a specific operation type. <get, gets, list, describe>', autocompletion=_complete_operation_type),
        patterns: Optional[List[str]] = typer.Option(None, "--pattern", '-p', show_default=False, help='UNIX pattern matching for generated parameters. Should be quoted. e.g. (-p "*prod-*")'),
        jmespath_selector: Optional[str]= typer.Option(None, "--jmespath-selector", '-js', show_default=False, help='JMESPath query selector to filter resulted data. Visit for tutorial: https://jmespath.org/tutorial.html'),
        debug: bool = typer.Option(False, "--debug", '-d', help='Enable debug messages.'),
        formatter: Optional[str]= typer.Option(None, "--format", '-f', show_default=False, help='Python f-string expression to generate a line for each item.'),
        list_contents: bool = typer.Option(False, "--list", '-l', help='Print the details of Service or Resource. Does not make requests.'),
        paginate: bool = typer.Option(False, "--screen", '-s', help='Open the data on a separate paginator on shell.'),
    ):
    if debug:
        set_log_level_at_runtime(logging.DEBUG)
    if list_contents:
        _list_service_or_resource(service, resource_node)
        return

    # vvv()
    # return
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
            # read all operations in given resource node 
            read_data = service_reader.read_resource_node(resource_node, match_patterns=patterns)
          
        else: # Operation is selected
            resource_node_obj = service_node.get_resource_node_by_name(resource_node)
            types_to_op_names = resource_node_obj.get_operation_types_and_names()
            supported_operation_types = list(types_to_op_names.keys())
            operation_name = types_to_op_names.get(operation, False)
            if not operation_name:
                console.print(f"[red bold]Given {operation} is not supported by {resource_node}. Try: {supported_operation_types}")
                return False
            read_data = service_reader.read_operation(resource_node, operation_name, match_patterns=patterns)
   
        if jmespath_selector:
            
            logger.debug(f"Using jmespath selector: {jmespath_selector} to query the returned data.")
            read_data = jmespath.search(jmespath_selector, read_data)
        
        if formatter:
            if read_data:
                for r_data in read_data:
                    console.print(formatter.format(**r_data))
                return read_data
            else:
                logger.debug(f"[red]No data read.[/] Failed to use --formats: '{formatter}'")
    
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
    