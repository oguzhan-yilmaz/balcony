try:
    from .utils import camel_case_split, compare_nouns, ifind_similar_names_in_list , icompare_two_token_lists, compare_two_camel_case_words, str_relations
    from .botocore_utils import *
    from .relations import RelationMap, FindRelationResultTypes
    from .reader import ServiceReader
    from .registries import ResourceNodeRegistry
    from .logs import get_logger, get_rich_console
except ImportError:
    from utils import camel_case_split, compare_nouns, ifind_similar_names_in_list , icompare_two_token_lists, compare_two_camel_case_words, str_relations
    from botocore_utils import *
    from relations import RelationMap, FindRelationResultTypes
    from reader import ServiceReader
    from registries import ResourceNodeRegistry
    from logs import get_logger, get_rich_console

from pprint import pprint
import json
import boto3
from itertools import product as cartesian_product
from enum import Enum
import copy
from termcolor import colored
from botocore.utils import ArgumentGenerator
from botocore.validate import validate_parameters
from botocore.hooks import EventAliaser
from botocore.model import OperationModel, ServiceModel
from rich.text import Text
from rich.panel import Panel
from rich.console import Group
from rich.layout import Layout
import jmespath
from abc import ABC, abstractmethod
# class AbstractResourceNode(ABC):
    
#     @abstractmethod
#     def get_resource_nodes(self): ...
    
logger = get_logger(__name__)


_resource_node_registry = ResourceNodeRegistry()
argument_generator = ArgumentGenerator()
console = get_rich_console()

class ResourceNode:
    def __init__(self, service_node: 'ServiceNode', name: str, operation_names: List[str]):
        self.service_node = service_node
        self.name = name
        self.operation_names = operation_names
        self._operation_models = {}


    # NOTE: +overrideable
    def define_extra_relations(self):
        return []
    
    # NOTE: +overrideable
    def get_operations_relations(self, operation_name:str, relation_map: RelationMap=None):
        resource_node = self
        if relation_map is None:
            relation_map = self.service_node.get_relation_map()
        required_parameter_names = resource_node.get_required_parameter_names_from_operation_name(operation_name)
        required_parameter_names_to_relations_map = {
            r_param_name:None 
            for r_param_name in required_parameter_names
        }
        
        if not required_parameter_names:
            # no required parameters
            logger.debug(f"NO REQUIRED PARAMETERS. [bold][blue]{self.service_node.name}[/].[green]{operation_name}[/][/] has no required parameters")
            return True, FindRelationResultTypes.NoRequiredParameters

        if len(required_parameter_names) == 1:
            # only one parameter exists
            selected_relations = None
            single_parameter_name = required_parameter_names[0]
            generated_relations_for_parameter = relation_map.get_parameters_generated_relations(single_parameter_name, operation_name)
            if not generated_relations_for_parameter:
                logger.debug(f"NO RELATIONS GENERATED. [bold][blue]{self.service_node.name}[/].[green]{operation_name}[/][/] has req parameter: {single_parameter_name}. {generated_relations_for_parameter=}")
                return False, FindRelationResultTypes.NoGeneratedParameters

            selected_relations = resource_node.find_best_relation_for_single_parameter(single_parameter_name, generated_relations_for_parameter)
            # required_parameter_names_to_relations_map[single_parameter_name]=selected_relations
            if selected_relations:
                logger.debug(f"SINGLE PARAMETER FOUND. [bold][blue]{self.service_node.name}[/].[green]{operation_name}[/][/] has req parameter: [bold]{single_parameter_name}[/]. Relation found: [yellow]{str_relations(selected_relations)}[/]")
                return selected_relations, FindRelationResultTypes.RelationsFound
            else:
                logger.debug(f"CAN'T DECIDE BTWN RELATIONS. [bold][blue]{self.service_node.name}[/].[green]{operation_name}[/][/] has req parameters: {required_parameter_names}.")
                return False, FindRelationResultTypes.CantDecideBetweenGeneratedParameters
        else:
            # multiple required parameters, zip and check
            # required_parameter_names = list(required_parameter_names_to_relations_map.keys())
            # temporary_parameters_to_relations_map = dict()
            for r_parameter_name in required_parameter_names:
                generated_relations_for_parameter = relation_map.get_parameters_generated_relations(r_parameter_name, operation_name)
                if generated_relations_for_parameter:
                    required_parameter_names_to_relations_map[r_parameter_name]=generated_relations_for_parameter
                # return False, FindRelationResultTypes.NoGeneratedParameters
                # selected_relations = resource_node.find_best_relation_for_single_parameter(r_parameter_name, generated_relations_for_parameter)
                # ignore relations to self

            _all_parameters_have_relations = [
                bool(_found_relations) 
                for _found_relations in required_parameter_names_to_relations_map.values()
                
            ]

            if not all(_all_parameters_have_relations):
                # all parameters doesnt have relations
                if any(_all_parameters_have_relations):
                    # some found but not all
                    partial_relations_str = ", ".join([
                        str_relations(_found_relations)
                        for _found_relations in required_parameter_names_to_relations_map.values()
                        if _found_relations
                    ])
                    logger.debug(f"NOT ALL RELATIONS FOUND. [bold][blue]{self.service_node.name}[/].[green]{operation_name}[/][/] has req parameter: {required_parameter_names}. Partially found relations: {partial_relations_str}")
                    return False, FindRelationResultTypes.SomeRelationsFoundButNotAll
                else:
                    # nothing found
                    logger.debug(f"NO RELATIONS FOUND. [bold][blue]{self.service_node.name}[/].[green]{operation_name}[/][/] has req parameter: {required_parameter_names}.")
                    return False, FindRelationResultTypes.NoRelations
            
            def check(list_of_relations):
                if not list_of_relations:
                    return False
                first_operation_name = list_of_relations[0].get('operation_name')
                return all([l_o_r.get('operation_name')==first_operation_name for l_o_r in list_of_relations])
       
            possible_relation_combinations = None
            relation_matrix = list(required_parameter_names_to_relations_map.values())
            if relation_matrix:
                relations_cartesian_product = cartesian_product(*relation_matrix)
                possible_relation_combinations = list(filter(check, relations_cartesian_product))            
            
            if not possible_relation_combinations:
                logger.debug(f"CAN'T DECIDE BTWN RELATIONS. [bold][blue]{self.service_node.name}[/].[green]{operation_name}[/][/] has req parameters: {required_parameter_names}.")
                return False, FindRelationResultTypes.CantDecideBetweenGeneratedParameters
                # TODO: add required parameters to attributes + making them available as relations. add metadata.
            
            # find common target_operation relations across the permutation.
            relation_chosen_from_possible_combinations = self.select_between_possible_relation_combinations_matrix(possible_relation_combinations)    
            if relation_chosen_from_possible_combinations:
                logger.debug(f"MULTIPLE PARAMETERS FOUND. [bold][blue]{self.service_node.name}[/].[green]{operation_name}[/][/] has req parameters: {required_parameter_names}. Relations found: {str_relations(relation_chosen_from_possible_combinations)}")
                return relation_chosen_from_possible_combinations, FindRelationResultTypes.RelationsFound
            else:
                logger.debug(f"CAN'T DECIDE BTWN RELATIONS. [bold][blue]{self.service_node.name}[/].[green]{operation_name}[/][/] has req parameters: {required_parameter_names}.")
                return False, FindRelationResultTypes.CantDecideBetweenGeneratedParameters

    # NOTE: +overrideable
    def generate_jmespath_selector_from_relations(self, operation_name, relation_list):
        _for_all_the_responses = '[*].'
        _flatten_two_times = '[][]'
        if not relation_list:
            return False
        # [*].Stacks[*].{StackName: StackName, age: age}[] -> [*].Stacks[*].StackName[][]
        # [*].Stacks[*].StackName[], [*].Stacks[*].Description[]  
        target_shape_and_min_nested_target_paths = None
        # TODO: if type is list, do something different!!
        if len(relation_list) == 1:
            relation = relation_list[0]
            selected_target_path = min(relation.get('target_path').split(','), key=lambda tp: tp.count('.'))
            target_shape_and_min_nested_target_paths = [
                (relation.get('target_shape_name'), selected_target_path)
            ]
        else:
            # multiple relations
            # all relations point to same operation_name
            target_shape_and_min_nested_target_paths = [    
                (
                    relation.get('target_shape_name'), 
                    min(
                        relation.get('target_path').split(','), 
                        key=lambda tp: tp.count('.')
                    )
                )
                for relation in relation_list
            ]
            # all_selected_target_paths_same_depth = False
            # if len(relations_and_min_nested_target_paths) >= 2:

            # ensure target paths are same deep nested
            first_target_shape_and_target_path, *rest_of_target_shape_and_target_path = target_shape_and_min_nested_target_paths
            _, first_target_path = first_target_shape_and_target_path
            first_target_path_deepness = first_target_path.count('.')
            first_target_path_before_last_attribute = first_target_path.rsplit('.', maxsplit=1)[0]
            all_selected_target_paths_same_depth = all([
                r_target_path.count('.') == first_target_path_deepness \
                    and r_target_path.rsplit('.', maxsplit=1)[0] == first_target_path_before_last_attribute
                for _, r_target_path in rest_of_target_shape_and_target_path
            ])
                    
            if not all_selected_target_paths_same_depth:
                logger.debug(f"[red]DOES NOT START WITH same json nest: {target_shape_and_min_nested_target_paths}")
                return False
                
        jmespath_nested_selector = None
        
        # if len(target_shape_and_min_nested_target_paths) == 1:
        #     jmespath_nested_selector
        # else:
        _jmespath_selectors_list = []
        before_last_attr = None
        for target_shape, target_path in target_shape_and_min_nested_target_paths:
            if '.' not in target_path:
                target_path = f".{target_path}"
            before_last_attr, last_attribute = target_path.rsplit('.', maxsplit=1)
                
            jmespath_nested_selector = f"{target_shape}: {last_attribute}"
            _jmespath_selectors_list.append(jmespath_nested_selector)
        if not before_last_attr:
             before_last_attr = ''
        jmespath_nested_selector = before_last_attr+'.{'+', '.join(_jmespath_selectors_list)+'}'
        jmespath_nested_selector
        flattened_jmespath_nested_selector = f"{_for_all_the_responses}{jmespath_nested_selector}{_flatten_two_times}"
        return flattened_jmespath_nested_selector

    # NOTE: +overrideable
    def _generate_raw_api_parameters_from_operation_data(self, operation_name, relations_of_operation, related_operations_data):
        resource_node = self
        generated_jmespath_nested_selector = resource_node.generate_jmespath_selector_from_relations(operation_name, relations_of_operation)
        if not generated_jmespath_nested_selector:
            logger.debug(f"CAN'T GENERATE JMESPATH SELECTOR: {resource_node.name} {operation_name} {generated_jmespath_nested_selector}")
            return False
        logger.debug(f"JMESPATH SELECTOR GENERATED: [blue]{generated_jmespath_nested_selector}[/], target operation: [bold][blue][{resource_node.name}[/].[green]{operation_name}[/]]")

        if not related_operations_data:
            logger.debug(f"NO OPERATION DATA FOUND. {related_operations_data=}")

        raw_api_parameters_list = jmespath.search(generated_jmespath_nested_selector, related_operations_data)
        
        if raw_api_parameters_list == []:
            # successfull jmespath search that yielded no results. operation data might be empty
            return raw_api_parameters_list
        elif not raw_api_parameters_list:
            logger.debug(f"CANT GENERATE API PARAMETERS LIST WITH [bold][red]{generated_jmespath_nested_selector}[/] {related_operations_data=}")
            return False
        
        return raw_api_parameters_list
    
    # NOTE: +overrideable
    def create_valid_api_parameters_list(self, operation_name, related_operations_data, relations_of_operation, raw_api_parameters_list ):
        operation_model = self.get_operation_model(operation_name)
        required_parameter_names = self.get_required_parameter_names_from_operation_name(operation_name)

        input_shape = get_input_shape(operation_model)
        generated = {}
        
        if input_shape:
            generated = argument_generator.generate_skeleton(input_shape)
        
        result = {}

        for r_parameter_name in required_parameter_names:
            r_key = find_key_in_dict_keys(r_parameter_name, generated)
            if r_key:
                result[r_key] = generated[r_key]
                
        # handle MaxResults
        max_results_value = get_max_results_value_from_shape(input_shape)
        max_results_key = find_key_in_dict_keys('maxresults', generated)
        if max_results_key and max_results_value:
            result[max_results_key]=max_results_value
        # sometimes MaxResults can be seen as non required parameter, but in fact is
        if not required_parameter_names:
            return [result]
        
        
        search_to_target_names = {relation.get('target_shape_name'):relation.get('search_shape_name') for relation in relations_of_operation}
        
        generated_api_params = []
        if raw_api_parameters_list == False:
            # TODO: add logic here
            logger.debug(f"FAILED TO CREATE VALID API PARAMETERS. Required Parameters are: [bold]{required_parameter_names}[/]")
            return False
        for raw_api_parameter_dict in raw_api_parameters_list:
            result_copy = copy.deepcopy(result)
            for raw_key in raw_api_parameter_dict.keys():
                found_parameter_key = find_key_in_dict_keys(raw_key, result_copy)
                if not found_parameter_key:
                    # search to target name
                    new_key = find_key_in_dict_keys(raw_key, search_to_target_names)
                    if new_key:
                        found_parameter_key = find_key_in_dict_keys(search_to_target_names[new_key], result_copy)
                result_copy[found_parameter_key] = raw_api_parameter_dict[raw_key]
            generated_api_params.append(result_copy)
        # Handle NextToken and DryRun
        # dry_run_key_name = find_key_in_dict_keys('dryrun', generated)
        # generated.pop(dry_run_key_name)
        # next_token_key_name = find_key_in_dict_keys('nexttoken', generated)
        # generated.pop(next_token_key_name)
        # generated
        # # handle multiple required parameters
        # generated_api_params_list = []
        # for r_parameter_name in required_parameter_names:
        #     r_parameter_name_key = find_key_in_dict_keys(r_parameter_name, generated)
        #     r_parameter_value = generated.get(r_parameter_name_key)
        #     # if type
            
        #     # result[r_parameter_name_key] = ?
        # generated
        return generated_api_params
    
    # NOTE: +overrideable
    def generate_api_parameters_from_operation_data(self, operation_name, relations_of_operation, related_operations_data):
        resource_node = self
        resource_node_name = resource_node.name
        no_required_parameters = relations_of_operation == []

        if no_required_parameters:
            # Even though we know there are no required parameters, 
            # some parameters like MaxResults must be filled.
            api_parameters = resource_node.create_valid_api_parameters_list(operation_name, related_operations_data, [], [])
            return api_parameters

        related_operations_data
        raw_api_parameters_list = self._generate_raw_api_parameters_from_operation_data(operation_name, relations_of_operation, related_operations_data)
                
        api_parameters_list = resource_node.create_valid_api_parameters_list(operation_name, related_operations_data, relations_of_operation, raw_api_parameters_list)
        return api_parameters_list
    
    def print_operation(self, operation_name):
        operation_panel = self._rich_operation_details_panel(operation_name)
        console.print(operation_panel)

    def _rich_operation_details_panel(self, operation_name):
        
        operation_model = self.get_operation_model(operation_name)
        input_shape = get_input_shape(operation_model)
        output_shape = operation_model.output_shape
        
        input_shape_tree = Text("[yellow]No Input Shape Found")
        if input_shape:
            input_shape_tree = generate_rich_tree_from_shape(input_shape)
        output_shape_tree = generate_rich_tree_from_shape(output_shape)
        layout = Layout()
        layout.split_row(
            Panel(input_shape_tree, title='[yellow]Input Shape'),# subtitle=get_shape_name(input_shape)),
            Panel(output_shape_tree, title='[yellow]Output Shape'),# subtitle=get_shape_name(output_shape)),
        )
      
        required_parameters = self.get_required_parameter_names_from_operation_name(operation_name)
        _title = f"Operation: [green][bold]{operation_name}[/]"
        if required_parameters:
            _title = f"{_title}   [white][Required: {', '.join(required_parameters)}]"
        operation_panel = Panel(layout, title=_title, highlight=True, title_align='left')
        return operation_panel


    # todo: move to Reader
    def select_between_possible_relation_combinations_matrix(self, possible_relation_combinations):
        if len(possible_relation_combinations)==1:
            return possible_relation_combinations[0]
        # each combination will have the same operation name
        # prefer using non-GET function
        # prefer the operation that has no required parameters
        combination_index_to_score_map = {str(i):0 for i in range(len(possible_relation_combinations))}
        
        for i, relation_combination in enumerate(possible_relation_combinations):
            current_combination_point = 0
            combinations_operation_name = relation_combination[0].get('operation_name') # promised to all have same operation
            
            # negative point if it has required parameters
            combinations_required_parameters = self.get_required_parameter_names_from_operation_name(combinations_operation_name)
            current_combination_point -= len(combinations_required_parameters)
            
            # negative point if its a get function, we'd like to prefer list or describe functions
            if combinations_operation_name.lower().startswith('get'):
                current_combination_point -= 1
            
            combination_index_to_score_map[str(i)] = current_combination_point
        selected_index_str, selected_score = max(combination_index_to_score_map.items(), key=lambda index_and_score: index_and_score[1])
        selected_combination = possible_relation_combinations[int(selected_index_str)]
        
        return selected_combination

    # todo: move to Reader
    def select_between_possible_relation_combinations_list(self, possible_relation_list):
        if len(possible_relation_list)<1:
            return False
        if len(possible_relation_list)==1:
            return possible_relation_list[0]
        # each combination will have the same operation name
        # prefer using non-GET function
        # prefer the operation that has no required parameters
        combination_index_to_score_map = {str(i):0 for i in range(len(possible_relation_list))}
        
        get_operation_count  = [p_rel.get('operation_name').startswith('Get') for p_rel in possible_relation_list].count(True)
        for i, relation_dict in enumerate(possible_relation_list):
            current_combination_point = 0
            relations_operation_name = relation_dict.get('operation_name') # promised to all have same operation
            
            # negative point if it has required parameters
            combinations_required_parameters = self.get_required_parameter_names_from_operation_name(relations_operation_name)
            current_combination_point -= len(combinations_required_parameters)
            
            # negative point if its a get function, we'd like to prefer list or describe functions
            if get_operation_count <= 1 and relations_operation_name.lower().startswith('get'):
                current_combination_point -= 1
            
            combination_index_to_score_map[str(i)] = current_combination_point
        selected_index_str, selected_score = max(combination_index_to_score_map.items(), key=lambda index_and_score: index_and_score[1])
        selected_combination = possible_relation_list[int(selected_index_str)]
        
        return selected_combination
    
    # todo: move to Reader
    def find_best_relation_for_single_parameter(self, parameter_name, relation_list):
        _parameter_name_tokens = camel_case_split(parameter_name)
        non_id_parameter_tokens = [
            p_token for p_token in _parameter_name_tokens
            if p_token.lower() not in IDENTIFIER_NAMES
        ]
        
        # if not non_id_parameter_tokens:
        #     # only contains id 
        #     non_id_parameter_tokens  =_parameter_name_tokens

        same_resource_name_relations = []
        for relation_dict in relation_list:
            operation_name = relation_dict.get('operation_name')
            operation_verb, *operation_name_tokens = camel_case_split(operation_name)
            # relation_dict.update({'operation_verb': operation_verb, 'operation_name_tokens': operation_name_tokens})
            # TODO: here
            all_tokens_match = icompare_two_token_lists(
                non_id_parameter_tokens, operation_name_tokens)
            if all_tokens_match:
                same_resource_name_relations.append(relation_dict)
                    
        # what we are left with is different operations names 
        selected_relation = self.select_between_possible_relation_combinations_list(same_resource_name_relations)
        if selected_relation:
            return [selected_relation]
        return False
    
    def get_required_parameter_names_from_operation_name(self, operation_name):
        
        operation_model = self.get_operation_model(operation_name)
        input_shape = get_input_shape(operation_model)
        if not input_shape:
            return []
        required_parameter_names = getattr(input_shape, 'required_members', False)
        max_results_key = find_key_in_dict_keys('maxresults', required_parameter_names)
        if max_results_key:
            required_parameter_names.remove(max_results_key)
        return required_parameter_names
    
    def get_all_required_parameter_names(self):
        all_required_names = []
        for operation_name in self.operation_names:
            required_shapes = self.get_required_parameter_names_from_operation_name(
                operation_name)
            all_required_names.extend(required_shapes)
        return all_required_names
    
    def get_operation_model(self, operation_name: str) -> OperationModel:
        """client._service_model"""
        if operation_name in self._operation_models:
            return self._operation_models[operation_name]
        service_model = self.service_node.get_service_model()
        operation_model = service_model.operation_model(operation_name)
        self._operation_models[operation_name] = operation_model
        return operation_model

    def json(self):
        return {
            "service_node_name": self.service_node.name,
            "name": self.name,
            "operation_names": self.operation_names
        }

    def __str__(self):
        # return f"[{self.service_node.name}.{self.name}]"
        return f"[{self.name}]"

    def __rich__(self):
        return 'ss'
 
 


class ServiceNode:
    def __init__(self, name, session):
        self.name = name
        self.session = session
        self.client = self.session.client(self.name)
        self.resource_nodes = None
        self._relation_map = None
        self._reader = None
        self._read_operation_name_to_tokens_map = None


    def read(self, resource_node_name):
        reader = self.get_service_reader()
        return reader.read_resource_node(resource_node_name)
    
    def get_service_reader(self):
        if not self._reader:
            self._reader = ServiceReader(self)
        return self._reader

    def print_resource_node(self, resource_node_name):
        # TODO: check if resource node exists
        operations_panel = self._get_operation_details_panel(resource_node_name)
        if operations_panel:
            console.print(operations_panel)
        
    def _get_operation_details_panel(self, resource_node_name):
        resource_node =  self.get_resource_node_by_name(resource_node_name)
        if not resource_node:
            return False
        panels_for_operations = [
            resource_node._rich_operation_details_panel(operation_name)
            for operation_name in resource_node.operation_names
        ]

        operations_group = Group(
            *panels_for_operations
        )
        return Panel(operations_group, title=f'Resource Node: [blue][bold]{resource_node.name} ', title_align='left')
        
    def get_resource_node_by_name(self, resource_node_name):
        if not resource_node_name:
            return False
        
        for r_node in self.get_resource_nodes():
            # FIXME: laterr
            # if r_node.name == resource_node_name:
            if icompare_two_camel_case_words(r_node.name, resource_node_name):
                return r_node
        return False
    
    def json(self):
        return {
            "service_name": self.name,
            # TODO:
        }

    def find_resource_node_by_operation_name(self, operation_name):
        for r_node in self.get_resource_nodes():
            if operation_name in r_node.operation_names:
                return r_node
        return None

    def get_relation_map(self):
        if self._relation_map is not None:
            return self._relation_map
        self._relation_map = RelationMap(self)
        return self._relation_map

    def get_resource_nodes(self):
        if self.resource_nodes is None:
            self.resource_nodes = self._generate_resource_nodes()
        return self.resource_nodes

    def create_resource_node(self, **kwargs):
        service_name = self.name
        resource_node_name = kwargs.get('name', False)
        _ResourceNodeClass = ResourceNode
        if not resource_node_name:
            logger.debug(f"A resource name must be provided on creation.", extra=kwargs)
            raise Exception('ResourceNode name must be provided.')
        _custom_cls_for_resource_node = _resource_node_registry.find_custom_class_for_resource_node(service_name, resource_node_name)
        if _custom_cls_for_resource_node:
            # print(_custom_cls_for_resource_node, 'is used for ', service_name, resource_node_name)
            logger.debug(f"Registry: {_custom_cls_for_resource_node} class is used for  [bold][green]{service_name}[/].[blue]{resource_node_name}")
            _ResourceNodeClass = _custom_cls_for_resource_node
        return _ResourceNodeClass(**kwargs)
    
    def _generate_resource_nodes(self):
        generated_resouce_nodes = []
        op_name_to_tokens_map = self.get_read_operation_name_to_tokens_map()
        resource_name_to_operations_map = {}
        for operation_name, op_name_tokens in op_name_to_tokens_map.items():
            verb, *resource_name_list = op_name_tokens
            resource_node_name = ''.join(resource_name_list)
            
            found_key = ifind_key_in_dict_keys(resource_node_name, resource_name_to_operations_map.keys())
            if found_key:
                # decide if we want to keep the plural or singular name
                
                sp_comparison = compare_nouns(resource_node_name, found_key)
                if sp_comparison == 's:p':
                    # swap the found_key with resource_node_name as dict key
                    resource_name_to_operations_map[resource_node_name] = [operation_name] + resource_name_to_operations_map[found_key]
                    resource_name_to_operations_map.pop(found_key)
                else:
                    resource_name_to_operations_map[found_key].append(operation_name)                
            else:
                resource_name_to_operations_map[resource_node_name] = [
                    operation_name]

        # createt the resource nodes
        for resource_node_name, operations_list in resource_name_to_operations_map.items():
            created_resource_node = self.create_resource_node(
                service_node=self, 
                name=resource_node_name, 
                operation_names=operations_list
            )
            if created_resource_node:
                generated_resouce_nodes.append(created_resource_node)

        if len(generated_resouce_nodes) <= 1:
            return generated_resouce_nodes

        # TODO: decide if this should be kept
        # concat same names
        combined_resource_nodes = []
        _used_for_combining_resource_nodes = []

        for i, gen_resource_node in enumerate(generated_resouce_nodes[:-1]):
            if gen_resource_node in _used_for_combining_resource_nodes:
                continue
            for other_resource_node in generated_resouce_nodes[i+1:]:
                # FIXME: IMPORTANT
                if compare_two_camel_case_words(gen_resource_node.name, other_resource_node.name):
                    # select the shortest name, meaning singular
                    singular_named_resource_node = gen_resource_node
                    plural_named_resource_node = other_resource_node
                    if len(singular_named_resource_node.name) > len(plural_named_resource_node.name):
                        singular_named_resource_node, plural_named_resource_node = plural_named_resource_node, singular_named_resource_node
                    _used_for_combining_resource_nodes.append(
                        plural_named_resource_node)
                    singular_named_resource_node.operation_names.extend(
                        plural_named_resource_node.operation_names)

            if gen_resource_node not in _used_for_combining_resource_nodes:
                combined_resource_nodes.append(gen_resource_node)

        return combined_resource_nodes

    def get_read_operation_name_to_tokens_map(self):
        if self._read_operation_name_to_tokens_map is not None:
            return self._read_operation_name_to_tokens_map
        read_operation_names = self.get_read_operation_names()
        self._read_operation_name_to_tokens_map = self._generate_operation_name_to_tokens_map(
            read_operation_names)
        return self._read_operation_name_to_tokens_map

    def _generate_operation_name_to_tokens_map(self, operation_names:List[str]=None):
        if operation_names is None:
            operation_names = self.get_operation_names()

        op_name_to_tokens = {
            op_name: camel_case_split(op_name)
            for op_name in operation_names
        }
        return op_name_to_tokens

    def get_read_operation_names(self) -> List[str]:
        operation_names = self.get_operation_names()
        read_only_operation_names = [
            op_name
            for op_name in operation_names
            if any([op_name.startswith(read_verb) for read_verb in READ_ONLY_VERBS])
        ]
        return read_only_operation_names

    def get_service_model(self) -> ServiceModel:
        service_model = self.client._service_model
        return service_model

    def get_event_system(self) -> EventAliaser:
        event_system = self.client.meta.events
        return event_system

    def get_operation_names(self) -> List[str]:
        """Returns the `operation_names` defined in the boto client._service_model"""
        service_model = self.get_service_model()
        operation_names = service_model.operation_names
        return operation_names
