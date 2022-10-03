try:
    from .botocore_utils import get_shape_name, flatten_shape_to_its_non_collection_shape_and_target_paths, IDENTIFIER_NAMES
    from .logs import get_logger
    from .utils import icompare_two_camel_case_words
except ImportError:
    from botocore_utils import get_shape_name, flatten_shape_to_its_non_collection_shape_and_target_paths, IDENTIFIER_NAMES
    from logs import get_logger
    from utils import icompare_two_camel_case_words

import json
import os
from enum import Enum
logger = get_logger(__name__)

class FindRelationResultTypes(Enum):
    Success = 'Success'
    NoRequiredParameters = 'No required parameters'
    NoGeneratedParameters = 'NoParametersGenerated'
    CantDecideBetweenGeneratedParameters = 'CantDecideBetweenGeneratedParameters'
    SomeRelationsFoundButNotAll = 'SomeRelationsFoundButNotAll'
    NoRelations = 'NoRelations'
    RelationsFound = 'RelationsFound'
    InternalError = 'InternelError'

SUCCESSFUL_FIND_RELATION_RESULT_TYPES = (
    FindRelationResultTypes.Success,
    FindRelationResultTypes.NoRequiredParameters,
    FindRelationResultTypes.RelationsFound,
)
class RelationMap:
    def __init__(self, service_node):
        self.service_node = service_node
        self._relations_map = None

    def get_relations_map(self, refresh=False): # FIXME False
        if self._relations_map is not None and not refresh:
            return self._relations_map

        loaded_relations_map = self._load_relations_from_file()
        if loaded_relations_map and not refresh:
            self._relations_map = loaded_relations_map
            return self._relations_map

        generated_relations = self._generate_relation_map()
        self._relations_map = generated_relations
        self._save_relations_map_to_file()
        return self._relations_map

    # def check_parameter_name_inside_map(self, )
    def get_parameters_generated_relations(self, parameter_name, exclude_operation_name):
        relation_map = self.get_relations_map()
        relation_list = list()

        for map_parameter_name in relation_map.keys():
            # if compare_two_camel_case_words(map_parameter_name, parameter_name):
            if map_parameter_name.lower()==parameter_name.lower(): # FIXME: mixup of id, ids or other plural things. same for the operation names when creating a relation. GetThing and GetThings
                relation_list.extend(relation_map.get(map_parameter_name,[])) 

        if relation_list:
            non_self_referencing_relations = [
                relation_dict
                for relation_dict in relation_list
                if relation_dict.get('operation_name')!=exclude_operation_name
            ]
            return non_self_referencing_relations
        
        return False



    def find_best_relations_for_operations_parameters(self, operation_name):
        resource_node = self.service_node.find_resource_node_by_operation_name(operation_name)
        if not resource_node:
            return False
        relation_map = self
        result = resource_node.find_best_relations_for_operation(operation_name, relation_map)
        return result
            
    def _save_relations_map_to_file(self, relations_map=None, directory='relations'):
        service_name = self.service_node.name
        filepath = os.path.join(directory, f"{service_name}.json")
        relations_map = self.get_relations_map()
        with open(filepath, 'w') as file:
            json.dump(relations_map, file, indent=2, default=str)
        return True

    def _load_relations_from_file(self, directory='relations'):
        service_name = self.service_node.name
        filepath = os.path.join(directory, f"{service_name}.json")
        if not os.path.isfile(filepath):
            return False
        relations_map = None
        with open(filepath, 'r') as file:
            relations_map = json.load(file)
        return relations_map

    def _generate_resource_node_parameters_list(self, resource_nodes):
        _list = []
        for resource_node in resource_nodes:
            for operation_name in resource_node.operation_names:
                required_parameter_names = resource_node.get_required_parameter_names_from_operation_name(operation_name)
                _list.append({
                    'resource_node':resource_node,
                    'operation_name':operation_name,
                    'required_parameter_names':required_parameter_names
                })
        return _list


    def _generate_relation_map(self, **kwargs):
        resource_nodes = self.service_node.get_resource_nodes()
        # Create a list of dicts for each resource_node, operation_name and required_parameter_names
        operations_to_required_parameter_list = self._generate_resource_node_parameters_list(resource_nodes)
        
        # Get every unique required parameter names
        unique_required_shape_names = set()
        for _dict in operations_to_required_parameter_list:
            for r_param_name in _dict.get('required_parameter_names'):
                unique_required_shape_names.add(r_param_name)
        unique_required_shape_names_list = list(unique_required_shape_names)

        all_found_relations = []
        for __dict in operations_to_required_parameter_list:
            # unpack the dict
            resource_node=__dict.get('resource_node')
            operation_name =__dict.get('operation_name')
            required_parameter_names=__dict.get('required_parameter_names')
            
            operation_model = resource_node.get_operation_model(operation_name)
            output_shape = operation_model.output_shape
            
            resource_nodes_extra_relations = resource_node.define_extra_relations()
            if resource_nodes_extra_relations:
                all_found_relations.extend(resource_nodes_extra_relations)
            # for each member shape (attr.) of this operation 
            output_shape_and_target_paths = flatten_shape_to_its_non_collection_shape_and_target_paths(output_shape)
            # try to find it in the unique required parameter list
            for output_shape_and_target_path in output_shape_and_target_paths:
                shape = output_shape_and_target_path.shape
                target_path = output_shape_and_target_path.target_path
                shape_name = get_shape_name(shape)
                prefixed_naked_shape_name = None
                # if it's named only 'id', 'arn'... we append nodename in front of it and add it as an alias.
                if shape_name.lower() in IDENTIFIER_NAMES:
                    prefixed_naked_shape_name = f"{resource_node.name}{shape_name.capitalize()}"
                    all_found_relations.append({
                        'service_name':self.service_node.name,
                        'resource_node_name': resource_node.name,
                        'operation_name': operation_name,
                        'search_shape_name': prefixed_naked_shape_name,
                        'target_shape_name': shape_name,
                        'target_shape_type': shape.type_name,
                        'target_path': target_path,
                        'alias': True
                    })
                for required_shape_name in unique_required_shape_names_list:
                    # TODO: compare lower names
                    _match = icompare_two_camel_case_words(shape_name, required_shape_name)
                    if _match:
                        all_found_relations.append({
                            'service_name':self.service_node.name,
                            'resource_node_name': resource_node.name,
                            'operation_name': operation_name,
                            'search_shape_name': required_shape_name,
                            'target_shape_name': shape_name,
                            'target_shape_type': shape.type_name,
                            'target_path': target_path
                        })
        relations_map = {
            required_shape_name:[]
            for required_shape_name in unique_required_shape_names_list
        }
        def add_to_relations(relation):
            nonlocal relations_map # outer scope access
            alias = relation.get('alias', False)
            parameter_name = relation.get('search_shape_name')
            
            def is_key_in_relations_map(search_key):
                nonlocal relations_map # outer scope access
                map_keys = relations_map.keys()
                for map_key in map_keys:
                    # if compare_two_camel_case_words(map_key, search_key):
                    if map_key.lower()==search_key.lower(): # TODO: decide between these two
                        return map_key
                return False

            is_parameter_in_relation_map = is_key_in_relations_map(parameter_name)
            if is_parameter_in_relation_map:
                selected_parameter_name_key_in_the_map = is_parameter_in_relation_map
                relations_map[selected_parameter_name_key_in_the_map].append(relation)
            else:
                relations_map[parameter_name] = [relation]
        
              
        for found_rel in all_found_relations:
            add_to_relations(found_rel)
          
        return relations_map