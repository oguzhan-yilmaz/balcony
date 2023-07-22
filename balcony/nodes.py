from botocore_utils import (
    _flatten_shape_to_its_members_and_target_paths,
    get_shape_name,
)
from utils import (
    camel_case_split,
    compare_nouns,
    icompare_two_token_lists,
    compare_two_camel_case_words,
    str_relations,
    is_word_in_a_list_of_words,
    inform_about_develeoping_custom_resource_nodes,
)
from botocore_utils import (
    get_input_shape,
    annotate_shape_and_its_members_with_target_path,
    get_max_results_value_from_shape,
    find_key_in_dict_keys,
    generate_rich_tree_from_shape,
    icompare_two_camel_case_words,
    ifind_key_in_dict_keys,
    READ_ONLY_VERBS,
    IDENTIFIER_NAMES,
    cleanhtml,
)
from relations import RelationMap, Relation
from reader import ServiceReader
from registries import ResourceNodeRegistry
from config import get_logger, get_rich_console
from errors import Error

from typing import List, Dict, Tuple, Union
from botocore.utils import ArgumentGenerator
from botocore.hooks import EventAliaser
from botocore.model import OperationModel, ServiceModel
from rich.text import Text
from rich.panel import Panel
from rich.console import Group
from rich.padding import Padding
import jmespath

logger = get_logger(__name__)

_resource_node_registry = ResourceNodeRegistry()
argument_generator = ArgumentGenerator()
console = get_rich_console()
PAGINATION_TOKEN_KEYS = (
    "nexttoken",
    "continuationtoken",
    "marker",
    "nextcontinuationtoken",
)


class ResourceNode:
    def __init__(
        self, service_node: "ServiceNode", name: str, operation_names: List[str]
    ) -> None:
        self.service_node = service_node
        self.name = name
        self.operation_names = operation_names
        self._operation_models = {}

    def __init_subclass__(cls, service_name=None, name=None, **kwargs) -> None:
        """Initializes the custom subclasses of ResourceNode to ResourceNodeRegistry.

        Args:
            service_name (_type_, optional): Name of the AWS service. Defaults to None.
            name (_type_, optional): Name of the AWS Resource Node. Defaults to None.
        """
        super().__init_subclass__(**kwargs)
        if service_name and name:
            _resource_node_registry.register_class(cls, service_name, name)
        else:
            logger.debug(
                f'{cls.__name__} invalid! You must define "service_name" and "name"'
            )

    def get_operation_types_and_names(self) -> Dict[str, str]:
        operation_names = self.get_operation_names()
        types_to_operation_names = {}
        for op_name in operation_names:
            verb, *resource_node_name_tokens = camel_case_split(op_name)
            resource_node_name = "".join(resource_node_name_tokens)
            if verb.lower() == "describe":
                types_to_operation_names["describe"] = op_name
            if verb.lower() == "list":
                types_to_operation_names["list"] = op_name

            if verb.lower() == "get":
                if self.name != resource_node_name:
                    types_to_operation_names["gets"] = op_name
                else:
                    types_to_operation_names["get"] = op_name
        return types_to_operation_names

    def __str__(self) -> str:
        return f"ResourceNode({self.service_node.name}.{self.name})"

    def get_operation_names(self) -> List[str]:
        """Returns the available operation names in the ResourceNode.

        Returns:
            List[str]: Operation names tied to the ResourceNode
        """
        return self.operation_names

    # NOTE: +overrideable
    def define_extra_relations(self) -> Union[List[Dict], List[Relation]]:
        """Extra relations defined in the custom subclasses of ResourceNode

        Returns:
            Union[List[Dict], List[Relation]]: List of relations as dicts or Relation objects
        """
        return []

    # NOTE: +overrideable
    def get_operations_relations(
        self, operation_name: str
    ) -> Tuple[Union[List[Dict], bool], Union[Error, None]]:
        """_summary_

        Args:
            operation_name (str): Name of the operation.

        Returns:
            Tuple[Union[List[Dict], bool], Union[Error, None]]: Returns value and error.
                                                                True: No required parameters
                                                                False: Failure
                                                                List[Dict]: List of relations
        """

        resource_node = self
        relation_map = self.service_node.get_relation_map()
        required_parameter_names = (
            resource_node.get_required_parameter_names_from_operation_name(
                operation_name
            )
        )
        # required_parameter_names_to_relations_map = {
        #     r_param_name: None for r_param_name in required_parameter_names
        # }

        if not required_parameter_names:
            # no required parameters
            return True, None

        operation_markup = (
            f"[bold][green]{self.service_node.name}[/].[blue]{operation_name}[/][/]"
        )
        req_param_markup = f"[bold magenta]{', '.join(required_parameter_names)}[/]"

        if len(required_parameter_names) == 1:

            # only one parameter exists
            single_relation_list = None
            single_parameter_name = required_parameter_names[0]
            generated_relations_for_parameter = (
                relation_map.get_parameters_generated_relations(
                    single_parameter_name, operation_name
                )
            )
            if not generated_relations_for_parameter:
                logger.debug(
                    f"Failed to generate relations. {operation_markup} has a required parameters: {req_param_markup}"
                )
                inform_about_develeoping_custom_resource_nodes()
                return False, Error(
                    "failed to generate relations",
                    {
                        "required_parameter_names": required_parameter_names,
                        "service": self.service_node.name,
                        "resource_node": self.name,
                        "operation_name": operation_name,
                    },
                )

            single_relation_list = (
                resource_node.find_best_relation_for_single_parameter(
                    single_parameter_name, generated_relations_for_parameter
                )
            )
            if single_relation_list:
                logger.debug(
                    f"[green]Success finding relations.[/] {operation_markup} has a required parameter: {req_param_markup}. Relation found: [yellow]{str_relations(single_relation_list)}[/]"
                )
                return single_relation_list, None
            else:
                logger.debug(
                    f"Failed to choose the best relation for operation. {operation_markup} has required parameters: {req_param_markup}"
                )
                inform_about_develeoping_custom_resource_nodes()
                return False, Error(
                    "failed to choose the best relation",
                    {
                        "service": self.service_node.name,
                        "resource_node": self.name,
                        "operation_name": operation_name,
                        "generated_relations_for_parameter": generated_relations_for_parameter,
                    },
                )
        else:
            # multiple required parameters does not supported
            return False, Error(
                "multiple parameters - must be extended with a subclass",
                {
                    "service": self.service_node.name,
                    "resource_node": self.name,
                    "operation_name": operation_name,
                },
            )

    # NOTE: +overrideable
    def generate_jmespath_selector_from_relations(
        self, operation_name: str, relation_list: List[Dict]
    ) -> str:
        """
        Tries to generate the jmespath selector string from given relations. Could be overridden with custom subclasses.

        Args:
            operation_name (str): Name of the operation
            relation_list (List[Dict]): List of relations for the operation. Used to generate the jmespath selector.

        Returns:
            str: Jmespath selector string
        """
        if not len(relation_list) == 1:
            return False
        relation = relation_list[0]

        target_path = relation.target_path
        search_shape = relation.required_shape_name

        _for_all_the_responses = ""
        if not target_path.startswith("[*]."):
            _for_all_the_responses = "[*]."
        _flatten_two_times = "[][]"
        if not relation_list:
            return False

        if "." not in target_path:
            return False

        before_last_attr, last_attribute = target_path.rsplit(".", maxsplit=1)
        # name switch
        jmespath_curly_name_transform = f"{search_shape}: {last_attribute}"

        if not before_last_attr:
            before_last_attr = "[*]"

        # patching in the first part
        jmespath_selector = (
            before_last_attr + ".{" + jmespath_curly_name_transform + "}"
        )
        flattened_jmespath_nested_selector = (
            f"{_for_all_the_responses}{jmespath_selector}{_flatten_two_times}"
        )
        return flattened_jmespath_nested_selector

    # NOTE: +overrideable
    def _generate_raw_api_parameters_from_operation_data(
        self,
        operation_name: str,
        relations_of_operation: List[dict],
        related_operations_data: Union[Dict, List],
    ) -> List:
        """Generates the jmespath selector and search the data with it. Output is the list of api_parameters dictionaries.
        Only considers the required parameters(raw parameters) of the operation.
        > Note: Pagination parameters (e.g. `NextToken`, `MaxResults`) are not included.

        Args:
            operation_name (str): Name of the operation
            relations_of_operation (List[dict]): Relations of the operation
            related_operations_data (Union[Dict, List]): All related operations data

        Returns:
            List: List of required _raw_ API parameters, not including pagination parameters
        """
        if len(relations_of_operation) != 1:
            logger.debug(
                f"Not supported: jmespath selector genereation for multiple relations: {operation_name}"
            )
            inform_about_develeoping_custom_resource_nodes()
            return False, Error(
                "multiple parameters - must be extended with a subclass",
                {
                    "service": self.service_node.name,
                    "resource_node": self.name,
                    "operation_name": operation_name,
                },
            )

        direct_relation = relations_of_operation[0]
        direct_relation_op_markup = f"[bold][green]{direct_relation.resource_node_name}[/].[blue]{direct_relation.operation_name}[/][/]"

        resource_node = self
        generated_jmespath_nested_selector = (
            resource_node.generate_jmespath_selector_from_relations(
                operation_name, relations_of_operation
            )
        )
        if not generated_jmespath_nested_selector:
            logger.debug(
                f"Failed to generate JMESPATH selector for [bold][blue][{resource_node.name}[/].[green]{operation_name}[/]]"
            )
            inform_about_develeoping_custom_resource_nodes()
            return False, Error(
                "failed to generate jmespath selector",
                {
                    "service": self.service_node.name,
                    "resource_node": self.name,
                    "operation_name": operation_name,
                },
            )
        logger.debug(
            f"Successfuly generated JMESPATH Selector: '[bold]{generated_jmespath_nested_selector}[/]' to extract from {direct_relation_op_markup}"
        )

        if not related_operations_data:
            logger.debug(
                "Failed to find related operations data. Can't generate api parameters with the generated JMESPATH Selector"
            )
            inform_about_develeoping_custom_resource_nodes()

        # the first relation we will get
        direct_related_operation = direct_relation.operation_name
        directly_related_operation_data = related_operations_data.get(
            direct_related_operation
        )
        found_api_paramaters = jmespath.search(
            generated_jmespath_nested_selector, directly_related_operation_data
        )
        raw_api_parameters_list = found_api_paramaters
        # for r_api_param in found_api_paramaters:
        #     for r_api_p_value in r_api_param.values():
        #         if bool(r_api_p_value):
        #             raw_api_parameters_list.append(r_api_param)
        if raw_api_parameters_list == []:
            # successfull jmespath search that yielded no results. operation data might be empty
            return raw_api_parameters_list, Error(
                "related resources not found",
                {
                    "service": self.service_node.name,
                    "resource_node": self.name,
                    "operation_name": operation_name,
                },
            )
        elif not raw_api_parameters_list:
            logger.debug(
                f"CANT GENERATE API PARAMETERS LIST WITH [bold][red]{generated_jmespath_nested_selector}[/] {related_operations_data=}"
            )
            inform_about_develeoping_custom_resource_nodes()
            return False, Error(
                "failed to generate api parameters",
                {
                    "service": self.service_node.name,
                    "resource_node": self.name,
                    "operation_name": operation_name,
                },
            )

        return raw_api_parameters_list, None

    # NOTE: +overrideable
    def complement_api_parameters_list(
        self,
        operation_name: str,
        related_operations_data: Union[List, Dict],
        relations_of_operation: List[Dict],
        raw_api_parameters_list: List,
    ) -> List[Dict]:
        """Uses the `raw_api_parameters_list` and appends pagination parameters(MaxResults,...) to them.
            Also provided for easy subclass overriding.

        Args:
            operation_name (str): Name of the operation.
            related_operations_data (Union[List, Dict]): All related operations data
            relations_of_operation (List[Dict]): Relations of the operation
            raw_api_parameters_list (List): Generated raw API parameters

        Returns:
            List[Dict]: Valid API parameters to call the boto operation with
        """

        operation_model = self.get_operation_model(operation_name)
        required_parameter_names = (
            self.get_required_parameter_names_from_operation_model(operation_model)
        )

        input_shape = get_input_shape(operation_model)
        generated = {}

        # input shape may not exists, meaning no required parameters
        if input_shape:
            generated = argument_generator.generate_skeleton(input_shape)

        api_params = [{}]
        if raw_api_parameters_list:
            api_params = raw_api_parameters_list

        # handle MaxResults
        max_results_value = get_max_results_value_from_shape(input_shape)
        max_results_key = find_key_in_dict_keys("maxresults", generated)
        if max_results_key and max_results_value:
            for api_param in api_params:
                api_param.update({max_results_key: max_results_value})

        # sometimes MaxResults can be seen as non required parameter, but in fact is
        if not required_parameter_names:
            return api_params

        if raw_api_parameters_list == False:
            # this func expect raw_api_parameters_list present, only adds to prepared parameters
            logger.debug(
                f"FAILED TO CREATE VALID API PARAMETERS. Required Parameters are: [bold]{required_parameter_names}[/]"
            )
            inform_about_develeoping_custom_resource_nodes()
            return False

        return api_params

    # NOTE: +overrideable
    def generate_api_parameters_from_operation_data(
        self,
        operation_name: str,
        relations_of_operation: List[Dict],
        related_operations_data: Union[List, Dict],
    ) -> Tuple[Union[List, bool], Union[Error, None]]:
        """Generates API parameters for the given operation including pagination parameters.

        Args:
            operation_name (str): Name of the operation
            relations_of_operation (List[Dict]): Relations of the operation
            related_operations_data (Union[List, Dict]): All related operations data

        Returns:
            List: Generated API Parameters to call the Operations with
        """
        resource_node = self
        required_parameters = (
            resource_node.get_required_parameter_names_from_operation_name(
                operation_name
            )
        )
        no_relations = relations_of_operation == []
        no_required_parameters = required_parameters == []

        if no_required_parameters:
            # Even though we know there are no required parameters,
            # some parameters like MaxResults must be filled, if available.
            api_parameters = resource_node.complement_api_parameters_list(
                operation_name, related_operations_data, [], []
            )
            return api_parameters, None

        if no_relations:
            # todo
            pass
        # try to automatically generate the required parameters with relations
        (
            raw_api_parameters_list,
            raw_param_error,
        ) = self._generate_raw_api_parameters_from_operation_data(
            operation_name, relations_of_operation, related_operations_data
        )
        if raw_param_error is not None:
            # failed to generate raw api parameters list
            return False, raw_param_error

        # fill out the pagination parameters like MaxResults, ...
        api_parameters_list = resource_node.complement_api_parameters_list(
            operation_name,
            related_operations_data,
            relations_of_operation,
            raw_api_parameters_list,
        )
        if not api_parameters_list:
            return api_parameters_list, Error(
                "failed to generate api parameters",
                {
                    "service": self.service_node.name,
                    "resource_node": self.name,
                    "operation_name": operation_name,
                },
            )

        return api_parameters_list, None

    def print_operation(self, operation_name: str) -> None:
        operation_panel = self._rich_operation_details_panel(operation_name)
        console.print(operation_panel)

    def _rich_operation_details_panel(
        self, operation_name: str, remove_input_shape=False, remove_documentation=False
    ) -> Panel:

        operation_model = self.get_operation_model(operation_name)
        input_shape = get_input_shape(operation_model)
        output_shape = operation_model.output_shape
        input_shape_name = "No Input Shape Found"
        input_shape_tree = Text("No Input Shape Found")
        if input_shape:
            input_shape_tree = generate_rich_tree_from_shape(
                input_shape, remove_documentation=remove_documentation
            )
            input_shape_name = input_shape.name
        output_shape_tree = generate_rich_tree_from_shape(
            output_shape, remove_documentation=remove_documentation
        )

        operation_docs = cleanhtml(operation_model.documentation)

        panel_group = Group(
            Padding(f"[bold underline]Documentation:[/] {operation_docs}", (1, 2)),
            Panel(
                input_shape_tree,
                title=f"Input: [yellow]{input_shape_name}",
                title_align="left",
                padding=(1, 1),
            ),
            Panel(
                output_shape_tree,
                title=f"Output: [yellow]{output_shape.name}",
                title_align="left",
                padding=(1, 1),
            ),
        )

        if remove_input_shape:
            panel_group = Group(
                Padding(f"[bold underline]Documentation:[/] {operation_docs}", (1, 2)),
                Panel(
                    output_shape_tree,
                    title=f"Output: [yellow]{output_shape.name}",
                    title_align="left",
                    padding=(1, 1),
                ),
            )

        required_parameters = self.get_required_parameter_names_from_operation_name(
            operation_name
        )
        _title = f"[bold]Operation[/]: [magenta bold]{operation_name}[/]"
        if required_parameters:
            _title = f"{_title}   [white][Required: {', '.join(required_parameters)}]"
        operation_panel = Panel(
            panel_group, title=_title, highlight=True, title_align="left"
        )
        return operation_panel

    def find_best_relation_for_single_parameter(
        self, parameter_name: str, generated_relations_for_parameter: List[Dict]
    ) -> List[Dict]:
        if len(generated_relations_for_parameter) == 1:
            # found only one relation, no need to find the correct one
            return generated_relations_for_parameter

        # strip the required parameter name's identifiers
        _parameter_name_tokens = camel_case_split(parameter_name)
        non_id_parameter_tokens = [
            p_token
            for p_token in _parameter_name_tokens
            if p_token.lower() not in IDENTIFIER_NAMES
        ]

        # filter the gen. relation's resource name and required parameter name
        same_resource_name_relations = []
        for relation_obj in generated_relations_for_parameter:
            resource_node_name = relation_obj.resource_node_name
            resource_name_tokens = camel_case_split(resource_node_name)
            all_tokens_match = icompare_two_token_lists(
                non_id_parameter_tokens, resource_name_tokens
            )
            if all_tokens_match:
                same_resource_name_relations.append(relation_obj)

        if not same_resource_name_relations:
            return False

        # if there is only one relation with the same resource name, return it
        if len(same_resource_name_relations) == 1:
            return same_resource_name_relations

        # try to filter out the bad relations
        possible_relation_list = same_resource_name_relations
        relation_index_to_score_map = {
            str(i): 0 for i in range(len(possible_relation_list))
        }

        for i, relation_obj in enumerate(possible_relation_list):
            current_point = 0
            relations_operation_name = relation_obj.operation_name
            # promised to all have same operation
            # negative point if it has required parameters
            relations_required_parameters = (
                self.get_required_parameter_names_from_operation_name(
                    relations_operation_name
                )
            )
            current_point -= len(relations_required_parameters)

            # List verb gets +1 point
            if relations_operation_name.lower().startswith("list"):
                current_point += 1

            relation_index_to_score_map[str(i)] += current_point

        # select the best score
        selected_index_str, selected_score = max(
            relation_index_to_score_map.items(),
            key=lambda index_and_score: index_and_score[1],
        )
        selected_relation = possible_relation_list[int(selected_index_str)]

        if selected_relation:
            return [selected_relation]

        return False

    def get_pagination_token_output_to_parameter_name_mapping(
        self, operation_name: str
    ) -> Union[Dict[str, str], bool]:
        """Some Operations paginate their output using Pagination Token Parameters defined in `PAGINATION_TOKEN_KEYS`.

        Args:
            operation_name (str): Name of the operation in the resource_node.

        Returns:
            Union[Dict[str, str], bool]: False or A dictionary with `parameter_name` and `output_key` keys. e.g. `{"parameter_name":"nextToken", "output_key": "NextToken"}`.
        """
        resource_node: ResourceNode = self

        # find all parameter names that are in `PAGINATION_TOKEN_KEYS`, case insensitive
        parameter_names = [
            pn
            for pn in resource_node.get_all_parameter_names_from_operation_name(
                operation_name
            )
            if is_word_in_a_list_of_words(pn, PAGINATION_TOKEN_KEYS)
        ]

        #  find all output keys that are in `PAGINATION_TOKEN_KEYS`, case insensitive
        output_keys = [
            ok
            for ok in resource_node.get_all_output_keys_from_operation_name(
                operation_name
            )
            if is_word_in_a_list_of_words(ok, PAGINATION_TOKEN_KEYS)
        ]

        if output_keys and parameter_names:
            return {
                "parameter_name": parameter_names[0],
                "output_key": output_keys[0],
            }
        return False

    def get_required_parameter_names_from_operation_model(self, operation_model):
        input_shape = get_input_shape(operation_model)
        if not input_shape:
            return []
        required_parameter_names = getattr(input_shape, "required_members", False)
        max_results_key = find_key_in_dict_keys("maxresults", required_parameter_names)
        if max_results_key:
            required_parameter_names.remove(max_results_key)
        return required_parameter_names

    def get_all_parameter_names_from_operation_name(self, operation_name):
        operation_model = self.get_operation_model(operation_name)
        input_shape = get_input_shape(operation_model)
        if not input_shape:
            return []

        all_parameter_names = []
        input_shape_and_target_paths = _flatten_shape_to_its_members_and_target_paths(
            input_shape
        )
        for shape_and_target_path in input_shape_and_target_paths:
            shape_name = get_shape_name(shape_and_target_path.shape)
            if shape_name:
                all_parameter_names.append(shape_name)
        return all_parameter_names

    def get_all_output_keys_from_operation_name(self, operation_name):
        operation_model = self.get_operation_model(operation_name)
        output_shape = operation_model.output_shape
        if not output_shape:
            return []

        all_parameter_names = []
        input_shape_and_target_paths = _flatten_shape_to_its_members_and_target_paths(
            output_shape
        )
        for shape_and_target_path in input_shape_and_target_paths:
            shape_name = get_shape_name(shape_and_target_path.shape)
            if shape_name:
                all_parameter_names.append(shape_name)
        return all_parameter_names

    # TODO: memoization
    def get_required_parameter_names_from_operation_name(
        self, operation_name: str
    ) -> List[str]:
        operation_model = self.get_operation_model(operation_name)
        return self.get_required_parameter_names_from_operation_model(operation_model)

    def get_all_required_parameter_names(self) -> List[str]:
        all_required_names = []
        for operation_name in self.operation_names:
            required_shapes = self.get_required_parameter_names_from_operation_name(
                operation_name
            )
            all_required_names.extend(required_shapes)
        return all_required_names

    def get_operation_model(self, operation_name: str) -> OperationModel:
        if operation_name in self._operation_models:
            return self._operation_models[operation_name]
        service_model = self.service_node.get_service_model()
        operation_model = service_model.operation_model(operation_name)
        self._operation_models[operation_name] = operation_model
        return operation_model

    def json(self) -> Dict:
        return {
            "service_node_name": self.service_node.name,
            "name": self.name,
            "operation_names": self.operation_names,
        }

    def __str__(self) -> str:
        # return f"[{self.service_node.name}.{self.name}]"
        return f"[{self.name}]"


class YamlResourceNode(ResourceNode):
    def __init__(
        self,
        service_node: "ServiceNode",
        name: str,
        operation_names: List[str],
        yaml_config: Dict = None,
    ) -> None:
        """Initializes the YamlResourceNode with `yaml_config`.

        Args:
            service_node (ServiceNode): ServiceNode object
            name (str): Name of the ResourceNode
            operation_names (List[str]): Names of the ResourceNode's operations
            yaml_config (Dict, optional): Yaml Configuration defined in the `custom_yamls/*`. Defaults to None.
        """
        super().__init__(service_node, name, operation_names)
        self.yaml_config = yaml_config

    def define_extra_relations(self) -> Union[List[Dict], List[Relation]]:
        """Reads the Yaml Configuration for extra_relations defined, and returns the Relation objects.

        Returns:
            Union[List[Dict], List[Relation]]: Extra relations if they're defined in the Yaml configuration.
        """
        if not self.yaml_config.extra_relations:
            return []
        extra_relations = [
            Relation(**extra_relation.__dict__)
            for extra_relation in self.yaml_config.extra_relations
        ]
        return extra_relations

    def get_pagination_token_output_to_parameter_name_mapping(
        self, operation_name: str
    ) -> Union[Dict[str, str], bool]:
        """Tries to find the pagination token in the yaml_config for the given operation.

        ```json title="pagination_token_output_to_parameter_name_mapping example"
        {
            "parameter_name": "",
            "output_key": ""
        }
        ```

        Args:
            operation_name (str): AWS Operation name.

        Returns:
            Union[Dict[str, str], bool]: A dictionary with pagination token as key and parameter name as value.
            If no pagination token is defined, then returns False.
        """
        operations = self.yaml_config.operations
        for operation in operations:
            if operation_name == operation.operation_name:
                if operation.pagination_token_mapping:
                    return operation.pagination_token_mapping
        # if the operation is not the selected one, let the normal flow run.
        return super().get_pagination_token_output_to_parameter_name_mapping(
            operation_name
        )

    # NOTE: +overrideable
    def get_operations_relations(
        self, operation_name: str
    ) -> Tuple[Union[List[Dict], bool], Union[Error, None]]:
        """Finds the defined `explicit_relations` in the yaml_config for the given operation.


        Args:
            operation_name (str): AWS Operation Name.

        Returns:
            Tuple[Union[List[Dict], bool], Union[Error, None]]: Returns (value, error) tuple.
        """
        operations = self.yaml_config.operations
        for operation in operations:
            if operation_name == operation.operation_name:
                # cast schema to Relation objects
                if operation.explicit_relations:
                    explicit_relations = [
                        Relation(**rel_model.__dict__)
                        for rel_model in operation.explicit_relations
                    ]
                    return explicit_relations, None
        # if no explicit relations are defined, then call the ResourceNode method and return it
        return super().get_operations_relations(operation_name)

    def get_required_parameter_names_from_operation_name(
        self, operation_name: str
    ) -> List[str]:
        operations = self.yaml_config.operations
        for operation in operations:
            if operation_name == operation.operation_name:
                if operation.required_parameters:
                    required_parameters = operation.required_parameters
                    return required_parameters

        return super().get_required_parameter_names_from_operation_name(operation_name)

    # NOTE: +overrideable
    def generate_jmespath_selector_from_relations(
        self, operation_name: str, relation_list: List[Dict]
    ) -> str:
        """Finds the `jmespath_selector` definition in the `yaml_config` for the selected Operation.

        Args:
            operation_name (str): AWS Operation name.
            relation_list (List[Dict]): List of relations for the operation

        Returns:
            str: JMESPath selector string for extracting api parameters.
        """
        operations = self.yaml_config.operations
        for operation in operations:
            if operation_name == operation.operation_name:
                if operation.jmespath_selector:
                    js_selector = operation.jmespath_selector
                    return js_selector

        return super().generate_jmespath_selector_from_relations(
            operation_name, relation_list
        )

    # NOTE: +overrideable
    def complement_api_parameters_list(
        self,
        operation_name: str,
        related_operations_data: Union[List, Dict],
        relations_of_operation: List[Dict],
        raw_api_parameters_list: List,
    ) -> List:
        """After the api parameter genereation is done, this function will be called for each api_parameter generated to complement(add/remove parameters) it.

        ```yaml title="Example yaml_config def. for complement_api_parameters"
        # This option overrides the `complement_api_parameters_list` function.
        complement_api_parameters:
        # This option will be evoked after api parameter generation is
        # complete. You can use this feature to add key/value pairs,
        - action: add
          data:
            any: data
            is: OK
            to: add
        #  or remove keys from all generated API parameters.
        - action: remove
          keys:
            - remove
            - these
            - keys
        ```

        Args:
            operation_name (str): _description_
            related_operations_data (Union[List, Dict]): _description_
            relations_of_operation (List[Dict]): _description_
            raw_api_parameters_list (List): _description_

        Returns:
            List: _description_
        """
        precomplemented_api_params = super().complement_api_parameters_list(
            operation_name,
            related_operations_data,
            relations_of_operation,
            raw_api_parameters_list,
        )

        for operation in self.yaml_config.operations:
            if operation_name == operation.operation_name:
                if operation.complement_api_parameters:
                    # if the option is defined
                    for complement_action in operation.complement_api_parameters:
                        if complement_action.action == "add":
                            data = complement_action.data
                            for api_param_item in precomplemented_api_params:
                                api_param_item.update(data)

                        elif complement_action.action == "remove":
                            for api_param_item in precomplemented_api_params:
                                for remove_key in complement_action.keys:
                                    api_param_item.pop(remove_key, None)

        return precomplemented_api_params

    def generate_api_parameters_from_operation_data(
        self,
        operation_name: str,
        relations_of_operation: List[Dict],
        related_operations_data: Union[List, Dict],
    ) -> Tuple[Union[List, bool], Union[Error, None]]:
        """Finds the `override_api_parameters` in the `yaml_config` for the selected operation.

        Args:
            operation_name (str): AWS Operation name
            relations_of_operation (List[Dict]): Relation obj list for the Operation
            related_operations_data (Union[List, Dict]): Related operations are called beforehand and this is their data.

        Returns:
            Tuple[Union[List, bool], Union[Error, None]]: (value, error) tuple.
        """
        operations = self.yaml_config.operations
        for operation in operations:
            if operation_name == operation.operation_name:
                override_parameters = operation.override_api_parameters
                if override_parameters:
                    return override_parameters, None

        # if not defined, fall back to the default super class method
        return super().generate_api_parameters_from_operation_data(
            operation_name, relations_of_operation, related_operations_data
        )


class ServiceNode:
    def __init__(self, name, session):
        self.name = name
        self.session = session
        self.client = self.session.client(self.name)
        self.resource_nodes = None
        self._relation_map = None
        self._reader = None
        self._read_operation_name_to_tokens_map = None

    def get_client(self):
        return self.client

    def get_service_reader(self) -> ServiceReader:
        """Returns/creates the ServiceReader for the current ServiceNode

        Returns:
            ServiceReader: ServiceReader object for current ServiceNode
        """
        if not self._reader:
            self._reader = ServiceReader(self)
        return self._reader

    def print_resource_node(self, resource_node_name: str) -> None:
        # TODO: check if resource node exists
        operations_panel = self._get_operation_details_panel(resource_node_name)
        if operations_panel:
            console.print(operations_panel)

    def _get_operation_details_panel(self, resource_node_name: str) -> Panel:
        resource_node = self.get_resource_node_by_name(resource_node_name)
        if not resource_node:
            return False
        panels_for_operations = [
            resource_node._rich_operation_details_panel(operation_name)
            for operation_name in resource_node.operation_names
        ]

        operations_group = Group(*panels_for_operations)
        return Panel(
            operations_group,
            title=f"[bold]Resource Node: [blue]{resource_node.name} ",
            title_align="left",
        )

    def get_resource_node_by_name(self, resource_node_name: str) -> ResourceNode:
        """Searches the current ServiceNode for the given `resource_node_name`,
        and returns it.

        Args:
            resource_node_name (str): Name of the ResourceNode

        Returns:
            ResourceNode: The ResourceNode object, `False` if not found.
        """
        if not resource_node_name:
            return False

        for r_node in self.get_resource_nodes():
            # FIXME: laterr
            # if r_node.name == resource_node_name:
            if icompare_two_camel_case_words(r_node.name, resource_node_name):
                return r_node
        return False

    def __str__(self) -> str:
        return f"ServiceNode({self.name})"

    def json(self) -> Dict:
        return {
            "service_name": self.name,
            # TODO:
        }

    # TODO: memoization
    def find_resource_node_by_operation_name(self, operation_name: str) -> ResourceNode:
        """Traverses the ResourceNodes of the current ServiceNode and tries to find
        the ResourceNode that has the `operation_name` in it.

        Args:
            operation_name (str): Name of the operation

        Returns:
            ResourceNode: ResourceNode object that has the `operation_name`, or None.
        """
        for r_node in self.get_resource_nodes():
            if operation_name in r_node.operation_names:
                return r_node
        return None

    def get_relation_map(self) -> RelationMap:
        """Gets the relation map object.

        Returns:
            RelationMap: RelationMap object for the current ServiceNode
        """
        if self._relation_map is not None:
            return self._relation_map
        self._relation_map = RelationMap(self)
        return self._relation_map

    def get_resource_nodes(self) -> List[ResourceNode]:
        """Gets the available `ResourceNode`s of the current ServiceNode

        Returns:
            List[ResourceNode]: List of `ResourceNode`s available in the ServiceNode
        """
        if self.resource_nodes is None:
            self.resource_nodes = self._generate_resource_nodes()
        return self.resource_nodes

    def create_resource_node(self, **kwargs: Dict) -> ResourceNode:
        """Creates the ResourceNode object with the given `kwargs`.
        Uses the `ResourceNodeRegistry` to find the custom subclasses of the
        `ResourceNode` class, else defaults to use the ResourceNode class

        Raises:
            Exception: _description_

        Returns:
            ResourceNode: _description_
        """
        service_name = self.name
        resource_node_name = kwargs.get("name", False)
        _ResourceNodeClass = ResourceNode
        if not resource_node_name:
            logger.debug("A resource name must be provided on creation.", extra=kwargs)
            raise Exception("ResourceNode name must be provided.")
        _custom_cls_for_resource_node = (
            _resource_node_registry.find_custom_class_for_resource_node(
                service_name, resource_node_name
            )
        )
        if _custom_cls_for_resource_node:
            logger.debug(
                f"ResourceNodeRegistry: [bold][green]{service_name}[/].[blue]{resource_node_name}[/][/] has extended with custom class."
            )
            _ResourceNodeClass = _custom_cls_for_resource_node
            return _ResourceNodeClass(**kwargs)

        # try to find yaml config defined for this ResourceNode
        yaml_config_found = _resource_node_registry.search_yaml_config_registry(
            service_name, resource_node_name
        )
        if yaml_config_found:
            # add the yaml_config for the YamlResourceNode subclass initialization
            kwargs.update({"yaml_config": yaml_config_found})
            logger.debug(
                f"ResourceNodeRegistry: [bold][green]{service_name}[/].[blue]{resource_node_name}[/][/] has extended with custom yaml config."
            )
            yaml_resource_node_obj = YamlResourceNode(**kwargs)
            return yaml_resource_node_obj

        # return default ResourceNode class
        return _ResourceNodeClass(**kwargs)

    def _generate_resource_nodes(self) -> List[ResourceNode]:
        """Parses `botocore` client for the AWS service and generates ResourceNodes.
        Generated `ResourceNode`s can be subclasses of `ResourceNode`.

        Returns:
            List[ResourceNode]: List of generated `ResourceNode`s
        """
        generated_resouce_nodes = []
        op_name_to_tokens_map = self.get_read_operation_name_to_tokens_map()
        resource_name_to_operations_map = {}
        for operation_name, op_name_tokens in op_name_to_tokens_map.items():
            verb, *resource_name_list = op_name_tokens
            resource_node_name = "".join(resource_name_list)

            found_key = ifind_key_in_dict_keys(
                resource_node_name, resource_name_to_operations_map.keys()
            )
            if found_key:
                # decide if we want to keep the plural or singular name

                sp_comparison = compare_nouns(resource_node_name, found_key)
                if sp_comparison == "s:p":
                    # swap the found_key with resource_node_name as dict key
                    resource_name_to_operations_map[resource_node_name] = [
                        operation_name
                    ] + resource_name_to_operations_map[found_key]
                    resource_name_to_operations_map.pop(found_key)
                else:
                    resource_name_to_operations_map[found_key].append(operation_name)
            else:
                resource_name_to_operations_map[resource_node_name] = [operation_name]

        # createt the resource nodes
        for (
            resource_node_name,
            operations_list,
        ) in resource_name_to_operations_map.items():
            created_resource_node = self.create_resource_node(
                service_node=self,
                name=resource_node_name,
                operation_names=operations_list,
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
            for other_resource_node in generated_resouce_nodes[i + 1 :]:
                # FIXME: IMPORTANT
                if compare_two_camel_case_words(
                    gen_resource_node.name, other_resource_node.name
                ):
                    # select the shortest name, meaning singular
                    singular_named_resource_node = gen_resource_node
                    plural_named_resource_node = other_resource_node
                    if len(singular_named_resource_node.name) > len(
                        plural_named_resource_node.name
                    ):
                        singular_named_resource_node, plural_named_resource_node = (
                            plural_named_resource_node,
                            singular_named_resource_node,
                        )
                    _used_for_combining_resource_nodes.append(
                        plural_named_resource_node
                    )
                    singular_named_resource_node.operation_names.extend(
                        plural_named_resource_node.operation_names
                    )

            if gen_resource_node not in _used_for_combining_resource_nodes:
                combined_resource_nodes.append(gen_resource_node)

        return combined_resource_nodes

    def get_read_operation_name_to_tokens_map(self) -> Dict:
        """Generate `operation name to word tokens` map for the
        available read operations in the ServiceNode.

        Caches the output in the class attr. `_read_operation_name_to_tokens_map`.

        Returns:
            Dict: dictionary
        """
        if self._read_operation_name_to_tokens_map is not None:
            return self._read_operation_name_to_tokens_map
        read_operation_names = self.get_read_operation_names()
        self._read_operation_name_to_tokens_map = (
            self._generate_operation_name_to_tokens_map(read_operation_names)
        )
        return self._read_operation_name_to_tokens_map

    def _generate_operation_name_to_tokens_map(
        self, operation_names: List[str] = None
    ) -> Dict:
        if operation_names is None:
            operation_names = self.get_operation_names()

        op_name_to_tokens = {
            op_name: camel_case_split(op_name) for op_name in operation_names
        }
        return op_name_to_tokens

    def get_read_operation_names(self) -> List[str]:
        """Gets the operation names from the boto3 client and
        filters the operation names starting with `List`,`Get` or `Describe`.

        Returns:
            List[str]: Read Only operation names
        """
        operation_names = self.get_operation_names()
        read_only_operation_names = [
            op_name
            for op_name in operation_names
            if any([op_name.startswith(read_verb) for read_verb in READ_ONLY_VERBS])
        ]
        return read_only_operation_names

    def get_service_model(self) -> ServiceModel:
        """Returns the ServiceModel obj from boto3 client"""
        service_model = self.client._service_model
        return service_model

    def get_event_system(self) -> EventAliaser:
        """Returns the boto3 clients event system"""
        event_system = self.client.meta.events
        return event_system

    def get_operation_names(self) -> List[str]:
        """Returns the `operation_names` defined in the boto client._service_model"""
        service_model = self.get_service_model()
        operation_names = service_model.operation_names
        return operation_names
