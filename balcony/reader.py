try:
    from .utils import icompare_two_camel_case_words, str_relations, ifind_similar_names_in_list
    from .botocore_utils import READ_ONLY_VERBS
    from .relations import FindRelationResultTypes, SUCCESSFUL_FIND_RELATION_RESULT_TYPES
    from .logs import get_logger, get_rich_console
except ImportError:
    from utils import icompare_two_camel_case_words, str_relations, ifind_similar_names_in_list
    from botocore_utils import READ_ONLY_VERBS
    from relations import FindRelationResultTypes, SUCCESSFUL_FIND_RELATION_RESULT_TYPES
    from logs import get_logger, get_rich_console
from collections.abc import Iterable
import jmespath
from rich.progress import Progress, track, BarColumn, TextColumn, TaskProgressColumn, TimeRemainingColumn
from rich.table import Column
logger = get_logger(__name__)
console = get_rich_console()
class ServiceReader:
    def __init__(self, service_node):
        self.service_node = service_node
        self.response_data = {}

    def add_response_data(self, operation_name, response):
        if operation_name not in self.response_data:
            self.response_data[operation_name] = [response]
        else:
            self.response_data[operation_name].append(response)
            

    def verify_all_required_parameters_in_selected_relations(self, required_parameters, selected_relations):
        if not selected_relations or type(selected_relations) not in (list,tuple):
            return False
        parameter_to_relation_map = {required_parameter_name: None for required_parameter_name in required_parameters}
        for required_parameter_name in parameter_to_relation_map.keys():
            is_parameter_in_relation_map = any([
                icompare_two_camel_case_words(required_parameter_name, relation_dict.get('search_shape_name')) 
                 for relation_dict in selected_relations
            ])
            parameter_to_relation_map[required_parameter_name]=is_parameter_in_relation_map
        is_all_parameters_found_in_relations = all(parameter_to_relation_map.values())
        return is_all_parameters_found_in_relations
    
    
    def _call_operation(self, operation_name, api_parameters):
        # TODO: follow next tokens
        client = self.service_node.client
        from botocore.exceptions import ClientError
        try:
            # print(colored(f"{operation_name=} {api_parameters=}",'green'))
            logger.debug(f"CALLING OPERATION: [blue]{operation_name}[/] with parameters: {api_parameters}")
            response = client._make_api_call(operation_name, api_parameters)
            # response = None
            response
        except ClientError as e:
            # print(colored(str(e),'red'))
            logger.debug(f"FAILED: CALLING OPERATION. {operation_name} with parameters: {api_parameters}. Exception: {str(e)} ")
            return False
        
        resource_node = self.service_node.find_resource_node_by_operation_name(operation_name)
        if not resource_node:
            return False
        resource_node_name = resource_node.name
        self.add_to_node_data(resource_node_name, operation_name, response)
        response.pop('ResponseMetadata') # FIXME: add back
        response['__args__'] = api_parameters
        return response
    
    
        # if operation_data:
        #     new_api_params = jmespath.search(flattened_jmespath_nested_selector, operation_data)
        # operation_data
        # for 
        # # jmespath.search(f"[*].{target_path}[][]", operation_data)
        
        # target_paths = target_path.split(',')
        # all_found = []
        # for target_path in target_paths:
        #     # found =  
        #     jmespath.search(f"{_for_all_the_responses}{target_path}{_flatten_two_times}", response)
        #     if found:
        #         all_found.extend(found)
        # return all_found

    def search_operation_data(self, resource_node_name, operation_name):
        resource_node_exists = self.response_data.get(resource_node_name, False) != False
        if not resource_node_exists:
            return False
        result = self.response_data[resource_node_name].get(operation_name, False)
        return result
    
    def search_resource_node_data(self, resource_node_name):
        resource_node_data = self.response_data.get(resource_node_name, False) 
        return resource_node_data 
   
    
    def add_to_node_data(self, resource_node_name, operation_name, response):
        resource_node_exists = self.response_data.get(resource_node_name, False) != False
        
        if not resource_node_exists:
            self.response_data[resource_node_name] = {}
                
        if operation_name not in self.response_data[resource_node_name]:
            self.response_data[resource_node_name][operation_name] = [response]
        else:
            self.response_data[resource_node_name][operation_name].append(response)


    def read_operation(self, resource_node_name, operation_name, refresh=False):
        # if it has been read called already, return it

        resource_node = self.service_node.get_resource_node_by_name(resource_node_name)

        if refresh == True:
            pass # TODO: delete from reader
        already_existing_data = self.search_operation_data(resource_node.name, operation_name)
        
        if already_existing_data!=False and refresh == False:
            return already_existing_data
        
        
        if not resource_node:
            logger.debug(f"RESOURCE NODE NOT FOUND. While reading the {resource_node_name}.{operation_name}, Resource Node {resource_node_name} could not be loaded.")
            return False

        # add service_name and resource_node_name to relation dict
        relations_of_operation, relations_error = resource_node.get_operations_relations(operation_name, None)
        success_finding_relations = relations_error is None
        
        
        if not success_finding_relations:
            logger.debug(f"FAILED FINDING RELATIONS for OPERATION: [bold]{resource_node_name}.{operation_name}[/]. Failed to find relations: {relations_error}")
            return False
        
        if relations_of_operation == True:
            # no required parameters
            generated_api_parameters = resource_node.generate_api_parameters_from_operation_data(operation_name, [], {})
            
            if isinstance(generated_api_parameters, Iterable):
                for api_parameters in generated_api_parameters:
                    self._call_operation(operation_name, api_parameters)
            return self.search_operation_data(resource_node_name, operation_name)

        all_related_operations_data = {}
        for rel in relations_of_operation:
            rel_operation_data = self.read_operation(rel.get('resource_node_name'), rel.get('operation_name'), refresh=refresh)
            if not rel_operation_data:
                logger.debug(f"[red]FAILED TO FIND RELATED RESOURCES[/] from [bold]{resource_node_name}[/], while reading:  [bold]{rel.get('service_name')}.{rel.get('resource_node_name')}.{rel.get('operation_name')}[/] operation.")
                return False
          
            # gather all their related data, put it under a dict 
            all_related_operations_data.update({
                rel.get('operation_name'): rel_operation_data
            })

        # send the operations_data to resource_node to create valid_api_parameters
        generated_api_parameters = resource_node.generate_api_parameters_from_operation_data(operation_name, relations_of_operation, all_related_operations_data)

        if generated_api_parameters == []:
            logger.debug(f"FAILED TO AUTO-GENERATE API PARAMETERS. Related Resources couldn't found.")
        elif isinstance(generated_api_parameters, Iterable):
            # FIXME # for api_parameters in track(generated_api_parameters, description=f"Calling [green]{operation_name}[/] for [bold]{len(generated_api_parameters)}[/] resources...",transient=True, console=console):
            for api_parameters in generated_api_parameters:
                self._call_operation(operation_name, api_parameters)
        else:
            logger.debug(f"COULDN'T GENERATE API PARAMETERS. {resource_node_name}.{operation_name}. Generated Parameters: {generated_api_parameters}. Data: {all_related_operations_data}")
            
        return self.search_operation_data(resource_node_name, operation_name)


            
    def read_resource_node(self, resource_node_name):
        resource_node = self.service_node.get_resource_node_by_name(resource_node_name)
        if not resource_node:
            return False
        # print('\t', colored(resource_node_name,'yellow'))
        # read all operations
        
        for operation_name in resource_node.operation_names:
            # if operation_name != 'GetPasswordData':
            #     continue
            req_params = resource_node.get_required_parameter_names_from_operation_name(operation_name)
            # if req_params:
            req_params
            self.read_operation(resource_node_name, operation_name)
            # print('--------------------------------')
            # print()
          
        # return self.response_data.get(resource_node.name)
        return self.search_resource_node_data(resource_node.name)
            # if output == True:
            #     print(' >>>>>>>>>>>>>>>> NO PARAMETERS <<<<<<<<<<<<<<<<<<<<<<')


    # def get_operations_relations(self, resource_node_name, operation_name):
    #     resource_node = self.service_node.get_resource_node_by_name(resource_node_name)
    #     if not resource_node:
    #         return False, FindRelationResultTypes.InternalError
    #     relation_map = self.service_node.get_relation_map()
    #     required_parameters = resource_node.get_required_parameter_names_from_operation_name(operation_name)

        
    #     if not required_parameters:
    #         return True, FindRelationResultTypes.NoRequiredParameters
    #     else:
    #         # there are required parameters, try to find every relation for this operation
    #         relations_of_operation, relation_result_type = resource_node.find_best_relations_for_operation(operation_name, relation_map)
    #         is_all_parameters_found = self.verify_all_required_parameters_in_selected_relations(required_parameters, relations_of_operation)
    #         # return relations, relation_result_type
    #         if relation_result_type not in SUCCESSFUL_FIND_RELATION_RESULT_TYPES:
    #             # not succeeded
    #             return False, relation_result_type
    #         elif not is_all_parameters_found:
    #             return False, FindRelationResultTypes.SomeRelationsFoundButNotAll
    #         elif not relations_of_operation:
    #             return False, FindRelationResultTypes.NoRelations
    #         else:
    #             # success
    #             return relations_of_operation, FindRelationResultTypes.RelationsFound
             

        # if relation_result_type in SUCCESSFUL_FIND_RELATION_RESULT_TYPES:
            # FindRelationResultTypes.SomeRelationsFoundButNotAll
    # def list_available_methods(self):
    #     read_operation_names = self.service_node.get_read_operation_names()
    #     for r_ops_name in read_operation_names:
    #         for read_verb in READ_ONLY_VERBS:
    #             if r_ops_name.startswith(read_verb):

    #     pass
