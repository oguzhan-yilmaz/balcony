from botocore_utils import (
    get_shape_name,
    flatten_shape_to_its_non_collection_shape_and_target_paths,
    ShapeAndTargetPath,
)
from config import get_logger, BALCONY_RELATIONS_DIR
from utils import icompare_two_camel_case_words
from typing import List, Dict, Union
import json
import os
from dataclasses import dataclass


logger = get_logger(__name__)


@dataclass
class Relation:
    """Basic dataclass to hold the relation information."""
    service_name: str
    resource_node_name: str
    operation_name: str
    required_shape_name: str
    target_shape_name: str
    target_shape_type: str
    target_path: str

    def __str__(self):
        return f"{self.operation_name}:{self.required_shape_name}::{self.target_shape_name}"

    def __hash__(self):
        return hash(
            (
                self.service_name,
                self.resource_node_name,
                self.operation_name,
                self.required_shape_name,
                self.target_shape_name,
                self.target_shape_type,
                self.target_path,
            )
        )

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (
            self.service_name,
            self.resource_node_name,
            self.operation_name,
            self.required_shape_name,
            self.target_shape_name,
            self.target_shape_type,
            self.target_path,
        ) == (
            other.service_name,
            other.resource_node_name,
            other.operation_name,
            other.required_shape_name,
            other.target_shape_name,
            other.target_shape_type,
            other.target_path,
        )


class RelationMap:
    """
    RelationMap represents a mapping `ParameterName` to `Relations List`.
    `generate_relation_map()` function generates the RelationMap dictionary for given ServiceNode.

    ServiceNode caches the RelationMap dictionary to a file, because calculating it
    requires a lot of loops.

    ```json title="Example RelationMap dictionary"
     {
        "PolicyArn": [
            {
                "service_name": "iam",
                "resource_node_name": "Policy",
                "required_shape_name": "PolicyArn",
                "target_shape_name": "Arn",
                "target_shape_type": "string",
                "operation_name": "ListPolicies",
                "target_path": "Policies[*].Arn"
            }
        ],
    }
    ```
    """

    def __init__(self, service_node):
        self.service_node = service_node
        self._relations_map: Dict = None


    def serialize_relations_map(self, relations_map: Dict) -> Dict:
        """Serializes the RelationMap dictionary to a json serializable dictionary.

        Args:
            relations_map (Dict): RelationMap dictionary

        Returns:
            Dict: Json serialized dictionary
        """
        serialized_relations_map = dict()
        for parameter_name, relations in relations_map.items():
            serialized_relations = list()
            for relation in relations:
                serialized_relations.append(relation.__dict__)
            serialized_relations_map[parameter_name] = serialized_relations
        return serialized_relations_map

    def deserialize_relation_map(self, serialized_relations_map: Dict) -> Dict:
        """Deserializes the RelationMap dictionary from a json serialized dictionary.

        Args:
            serialized_relations_map (Dict): Json serialized dictionary

        Returns:
            Dict: RelationMap dictionary
        """
        relations_map = dict()
        for parameter_name, relations in serialized_relations_map.items():
            deserialized_relations = list()
            for relation in relations:
                deserialized_relations.append(Relation(**relation))
            relations_map[parameter_name] = deserialized_relations
        return relations_map


    def get_relations_map(self, refresh: bool = False) -> Dict:
        """Tries the fetch the cached RelationMap from file,
        or generates and saves it to file.

        Args:
            refresh (bool, optional): Disables cache. Defaults to False.

        Returns:
            Dict: `RelationMap` dictionary. parameter_name->[relations,] mapping.
        """
        if self._relations_map is not None and not refresh:
            return self._relations_map

        loaded_relations_map = self.load_relations_from_file()
        if loaded_relations_map and not refresh:
            self._relations_map = self.deserialize_relation_map(loaded_relations_map)
            return self._relations_map

        generated_relations = self.generate_relation_map()
        self._relations_map = generated_relations
        self.save_relations_map_to_file(self.serialize_relations_map(self._relations_map))
        return self._relations_map

    def get_parameters_generated_relations(
        self, parameter_name: str, exclude_operation_name: str
    ) -> List[Dict]:
        """Checks the `RelationMap` dictionary for the key: `parameter_name`
        to get the generated relations for the given parameter name.

        Args:
            parameter_name (str): Parameter name to search for its relations
            exclude_operation_name (str): Exclude the given operation_name across found relation dicts

        Returns:
            List[Dict]: List of relations
        """
        relation_map = self.get_relations_map()
        relation_list = list()

        for map_parameter_name in relation_map.keys():
            # if compare_two_camel_case_words(map_parameter_name, parameter_name):
            if map_parameter_name.lower() == parameter_name.lower():
                relation_list.extend(relation_map.get(map_parameter_name, []))

        if relation_list:
            non_self_referencing_relations = [
                relation_obj
                for relation_obj in relation_list
                if relation_obj.operation_name != exclude_operation_name
            ]
            return non_self_referencing_relations

        return False

    def save_relations_map_to_file(self, relations_map: List[Dict] = None) -> None:
        """Saves the generated relations map to `{BALCONY_RELATIONS_DIR}/{service_name}.json`

        Args:
            relations_map (List[Dict], optional): _description_. Defaults to None.
        """

        directory = BALCONY_RELATIONS_DIR
        service_name = self.service_node.name
        filepath = os.path.join(directory, f"{service_name}.json")
        if relations_map is None:
            relations_map = self.get_relations_map()
        logger.debug(
            f"Caching relations of [bold green]{service_name}[/] to {filepath}. Use: [bold]balcony clear-cache[/] to remove."
        )
        with open(filepath, "w") as file:
            json.dump(relations_map, file, indent=2, default=str)

    def load_relations_from_file(self) -> Union[dict, bool]:
        directory = BALCONY_RELATIONS_DIR
        service_name = self.service_node.name
        filepath = os.path.join(directory, f"{service_name}.json")
        if not os.path.isfile(filepath):
            return False
        relations_map = None
        try:
            with open(filepath, "r") as file:
                relations_map = json.load(file)
            logger.debug(
                f"Read cached relations of [bold green]{service_name}[/] from {filepath}. Use: [bold]balcony clear-cache[/] to remove."
            )
        except:  # noqa
            return False
        return relations_map

    def _generate_resource_node_parameters_list(self, resource_nodes):
        _list = []
        for resource_node in resource_nodes:
            for operation_name in resource_node.operation_names:
                required_parameter_names = (
                    resource_node.get_required_parameter_names_from_operation_name(
                        operation_name
                    )
                )
                _list.append(
                    {
                        "resource_node": resource_node,
                        "operation_name": operation_name,
                        "required_parameter_names": required_parameter_names,
                    }
                )
        return _list

    def generate_relation_map(self, **kwargs) -> Dict[str, list]:  # noqa
        """Generates the required parameter name to its relations mapping.
        ```json title="RelationMap structure"
        {
            "ParameterName1": [{}, {} ],
            "ParameterName2": [{}, ]
        }
        ```

        Returns:
            Dict[str, list]: Generated parameter names to Relation dict list map
        """
        resource_nodes = self.service_node.get_resource_nodes()
        # Create a list of dicts for each resource_node, operation_name and required_parameter_names
        # to be able to calculate the all required parameter names befgore generating the relations
        operations_to_required_parameter_list = self._generate_resource_node_parameters_list(resource_nodes) # noqa

        # Get every unique required parameter names
        unique_required_shape_names = set()
        for _dict in operations_to_required_parameter_list:
            for r_param_name in _dict.get("required_parameter_names"):
                unique_required_shape_names.add(r_param_name)
        unique_required_shape_names_list = list(unique_required_shape_names)

        # create the relations map beforehand, and add empty sets to each required parameter name
        relations_map = {
            required_shape_name: set()
            for required_shape_name in unique_required_shape_names_list
        }
        for __dict in operations_to_required_parameter_list:
            # loop through all resource nodes and their operations
            resource_node = __dict.get("resource_node")
            operation_name = __dict.get("operation_name")
            # required_parameter_names=__dict.get('required_parameter_names')

            operation_model = resource_node.get_operation_model(operation_name)
            output_shape_member = operation_model.output_shape

            resource_nodes_extra_relations = resource_node.define_extra_relations()
            if resource_nodes_extra_relations:
                for extra_relation in resource_nodes_extra_relations:
                    relation_obj = extra_relation
                    # cast dictionaries as a Relation object
                    if type(extra_relation) == dict:
                        relation_obj = Relation(**extra_relation)
                    # make sure the relation object is of type Relation
                    assert type(relation_obj) == Relation
                    if relation_obj.required_shape_name not in relations_map:
                        # make sure there's a set for this required shape name in the map
                        relations_map[relation_obj.required_shape_name] = set()
                    relations_map[relation_obj.required_shape_name].add(relation_obj)

            # get a list of output shape's members, with their target path
            output_shape_and_target_paths = (
                flatten_shape_to_its_non_collection_shape_and_target_paths(output_shape_member)
            )
            # for each member shape (attr.) of this operations output shape
            # try to find it in the unique required parameter list
            for output_shape_and_target_path in output_shape_and_target_paths:
                # unpack the shape and target path
                output_shape_member = output_shape_and_target_path.shape
                target_path = output_shape_and_target_path.target_path
                output_shape_member_name = get_shape_name(output_shape_member)

                # look for a match between eac required shape name
                # and the current output's member's shapes name
                for required_shape_name in unique_required_shape_names_list:
                    # check both names with plurality and camelcase insensitivity
                    _match = icompare_two_camel_case_words(
                        output_shape_member_name, required_shape_name
                    )
                    # if there's a required shape name found in any member, add it to the relations map
                    if _match:
                        relation_obj = Relation(
                            service_name=self.service_node.name,
                            resource_node_name=resource_node.name,
                            operation_name=operation_name,
                            required_shape_name=required_shape_name,
                            target_shape_name=output_shape_member_name,
                            target_shape_type=output_shape_member.type_name,
                            target_path=target_path,
                        )
                        # we'll be adding to a set, so we don't need to worry about duplicates
                        relations_map[required_shape_name].add(relation_obj)

        return relations_map
