
try:
    from .logs import get_logger, get_rich_console
except ImportError:
    from logs import get_logger, get_rich_console
    
from typing import List, Set, Dict, Tuple, Optional, Union
import textwrap

logger = get_logger(__name__)

def generate_py_code_for_customization(error, func_signature, help_text=''):
    error_msg = error.message
    resource_node = error.context.get('resource_node')
    service = error.context.get('service')
    operation_name = error.context.get('operation_name')
    err_heading = f"[red bold]Error: {error_msg}[/] for [bold][green]{service}[/].[blue]{resource_node}[/], operation: [yellow]{operation_name}[/][/]"
    file_line = f"[bold]File to edit: [green]balcony/custom_nodes/[/][blue]{service}.py[/][/]"
    class_line = f"class {resource_node}(ResourceNode, service_name='{service}', name='{resource_node}'):"
    # [reverse bold ]Please create a custom class and do something about this issue.[/]
        
    return textwrap.dedent(f"""
    [yellow bold reverse] ~~ HELP NEEDED! ~~[/]
    {err_heading}
    {help_text}
    
    [underline]{file_line}[/]
    
    {class_line}
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
        def {func_signature}:
            r = super().{func_signature}
            # manipulate `r` or return your own value
            return r         
    """, ).lstrip()

class Error(Exception):
    def __init__(self, message:str, context:Dict=None) -> None:            
        super().__init__(message) # Call the base class constructor
        self.message = message
        self.context = context
        error_log = self.create_error_log()
        if error_log:
            logger.debug(error_log)

    def create_error_log(self):
        error_msg = self.message

        if error_msg == "failed to generate relations":
            return generate_py_code_for_customization(self, 'get_operations_relations(operation_name)')
        elif error_msg == "failed to choose the best relation":
            return generate_py_code_for_customization(self, 'get_operations_relations(operation_name)')
        elif error_msg == "missing relations for parameter":
            return generate_py_code_for_customization(self, 'get_operations_relations(operation_name)')
        elif error_msg == "failed to generate api parameters":
            pass
        elif error_msg == "failed to generate jmespath selector":
            pass
        elif error_msg == "related resources not found":
            pass
        elif error_msg == "":
            pass
        elif error_msg == "":
            pass
        else:
            return False
