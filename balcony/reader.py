from config import get_logger, get_rich_console
from errors import Error
from utils import inform_about_develeoping_custom_resource_nodes
import fnmatch  # unix like pattern matching
from collections.abc import Iterable
from typing import List, Dict, Tuple, Optional, Union
from botocore.exceptions import ClientError


logger = get_logger(__name__)
console = get_rich_console()


class ServiceReader:
    """
    Upon initialization ServiceReaders defines a dictionary called `response_data`.
    Caled operations are stored in this dictionary.
    ```json title="self.response_data data hierarchy"
    {
        "ResourceNodeName": {
            "OperationName1": [{response1 dict}, {response2 dict}, ...],
            "OperationName2": [{response1 dict},...],
        }
    }
    ```
    """

    def __init__(self, service_node: "ServiceNode") -> None:
        """Initializes the reader with the `service_node`.

        Args:
            service_node (ServiceNode): Associated ServiceNode.
        """
        self.service_node = service_node
        self.response_data = {}

    def call_operation(
        self, resource_node: "ResourceNode", operation_name: str, api_parameter: Dict, follow_pagination : Optional[bool] = False # noqa  
    ) -> Union[dict, bool]:
        """Calls the given AWS operation with `api_parameter` dict.
        Saves the response data on `self.response_data` and returns it.

        Args:
            resource_node: Operations Resource Node
            operation_name (str): Name of the operation
            api_parameter (dict): dictionary to call the operation with
            follow_pagination (Optional[bool]): If the operations output is truncated follow the pagination tokens.

        Returns:
            Union[dict, bool]: `False` or response got from AWS API
        """
        client = self.service_node.client

        if not resource_node:
            return False

        try:
            logger.debug(
                f"Calling operation: [bold blue]{operation_name}[/] with api parameters: {api_parameter}"
            )
            response = client._make_api_call(operation_name, api_parameter)
            # check if the operation is paginated
            pagination_tokens = (
                resource_node.get_pagination_token_output_to_parameter_name_mapping(
                    operation_name
                )
            )
            if follow_pagination and pagination_tokens:
                # try to find the name of the operation you'd want to fill out
                # and where to find it from in the response
                pagination_parameter_name = pagination_tokens.get("parameter_name")
                pagination_output_key = pagination_tokens.get("output_key")
                # we may find out the operation is paginated, but the queried resource might not be much in quantity
                # so, response might not have a Pagination token, although the operation is paginated
                page_value_in_response = response.get(pagination_output_key, False)
                if page_value_in_response:
                    paginated_api_parameters = api_parameter.copy()
                    paginated_api_parameters[
                        pagination_parameter_name
                    ] = page_value_in_response
                    self.call_operation(
                        resource_node, operation_name, paginated_api_parameters, follow_pagination=follow_pagination
                    )
        except ClientError as e:
            logger.debug(
                f"[red bold]FAILED: Calling Operation[/]. {operation_name}({api_parameter}). Exception: {str(e)}"
            )
            return False

        # removing ResponseMetadata, it is not needed
        response.pop("ResponseMetadata")
        response["__args__"] = api_parameter
        self.add_to_node_data(resource_node.name, operation_name, response)
        return response

    def search_operation_data(
        self, resource_node_name: str, operation_name: str
    ) -> Union[List[dict], bool]:
        """Get the currently read and available operation data.

        Args:
            resource_node_name (str): Name of the ResourceNode
            operation_name (str): Name of the Operation

        Returns:
            Union[List[dict], bool]: `False` or Operations data
        """
        resource_node_exists = (
            self.response_data.get(resource_node_name, False) != False  # noqa
        )
        if not resource_node_exists:
            return False
        resource_data: Dict = self.search_resource_node_data(resource_node_name)  # type: ignore
        result = resource_data.get(operation_name, [])
        return result

    def search_resource_node_data(self, resource_node_name: str) -> Union[dict, bool]:
        """Gets all data available for the ResourceNode, including all of its operations.

        Args:
            resource_node_name (str): Name of the ResourceNode

        Returns:
            Union[dict, bool]: `False` or all operations data of the given ResourceNode
        """
        resource_node_data = self.response_data.get(resource_node_name, False)
        return resource_node_data

    def clear_operations_data(
        self, resource_node_name: str, operation_name: str
    ) -> None:
        """Refreshes the operations data to empty list.

        Args:
            resource_node_name (str): Name of the ResourceNode
            operation_name (str): Name of the Operation
        """
        resource_node_exists = (
            self.response_data.get(resource_node_name, False) != False  # noqa
        )
        if resource_node_exists:
            self.response_data[resource_node_name][operation_name] = []

    def add_to_node_data(
        self, resource_node_name: str, operation_name: str, response: dict
    ) -> None:
        """Adds boto3 api response to operations existing data.

        Args:
            resource_node_name (str): Name of the ResourceNode
            operation_name (str): Name of the Operation
            response (dict): boto API response dict
        """
        resource_node_exists = (
            self.response_data.get(resource_node_name, False) != False # noqa
        )

        if not resource_node_exists:
            self.response_data[resource_node_name] = {}

        if operation_name not in self.response_data[resource_node_name]:
            self.response_data[resource_node_name][operation_name] = [response]
        else:
            self.response_data[resource_node_name][operation_name].append(response)

    def read_operation(
        self,
        resource_node_name: str,
        operation_name: str,
        match_patterns: Optional[List[str]] = None,
        refresh: Optional[bool] = False,
        follow_pagination: Optional[bool] = False
    ) -> Tuple[Union[List, bool], Union[Error, None]]:
        """Reads the given operation.
        If the operation is called with generated parameters, `match_patterns` can be used to filter the generated parameters.

        Args:
            resource_node_name (str): Name of the Resource Node
            operation_name (str): Name of the Operation
            match_patterns (List[str], optional): UNIX style patterns to filter matching generated parameters. Defaults to None.
            refresh (bool, optional): Get the cached data or force re-reading the operation. Defaults to False.
            follow_pagination (bool, optional): Follow pagination tokens. If not only set True, one page call will be made.

        Returns:
            Tuple[Union[List, bool], Union[Error, None]]: _description_
        """
        # if it has been read called already, return it if refresh is not set
        operation_markup = (
            f"[bold][green]{self.service_node.name}[/].[blue]{operation_name}[/][/]"
        )
        logger.debug(f"[underline][bold]Reading[/] {operation_markup}[/]")

        resource_node = self.service_node.get_resource_node_by_name(resource_node_name)
        if not resource_node:
            logger.debug(
                f"Failed to find the Resource Node while reading the {operation_markup}."
            )
            return None
        if refresh == True:  # noqa
            # remove the operation data from the response data,
            self.clear_operations_data(resource_node_name, operation_name)
        already_existing_data = self.search_operation_data(
            resource_node.name, operation_name
        )

        if already_existing_data and refresh == False:  # noqa
            logger.debug(
                f"[green]{resource_node.name}[/].[blue]{operation_name}[/] is already read. Returning already available data."
            )
            return already_existing_data

        if not resource_node:
            logger.debug(
                f"Failed to find the Resource Node while reading the {operation_markup}."
            )
            return False

        # try to automatically find the relations for this operation
        (
            relations_of_operation,
            relations_error,
        ) = resource_node.get_operations_relations(operation_name)
        success_finding_relations = relations_error is None
        required_parameters = (
            resource_node.get_required_parameter_names_from_operation_name(
                operation_name
            )
        )
        req_param_markup = f"[bold magenta]{', '.join(required_parameters)}[/]"

        def api_parameters_match_pattern(
            api_parameters: List[dict], patterns: List[str]
        ) -> List[dict]:
            if not patterns:
                return api_parameters
            matched_parameters = []

            for api_param in api_parameters:
                has_api_param_added = False
                for api_param_value in api_param.values():
                    for pattern in patterns:
                        if (
                            not has_api_param_added
                            and fnmatch.fnmatch(api_param_value, pattern)
                            and api_param not in matched_parameters
                        ):
                            matched_parameters.append(api_param)
                            has_api_param_added = True
            return matched_parameters

        if not success_finding_relations:
            logger.debug(f"[red]Error: {relations_error}: {operation_markup}")
            logger.debug(
                f"Failed to find the Relations for operation, required parameters: {req_param_markup}"
            )
            inform_about_develeoping_custom_resource_nodes()
            return False, relations_error

        if (
            relations_of_operation == True  # noqa
        ):  # True means no required parameters, so no relations
            # no relations means there are no related operations
            (
                generated_api_parameters,
                generation_error,
            ) = resource_node.generate_api_parameters_from_operation_data(
                operation_name, [], {}
            )

            if generation_error is not None:
                logger.debug(
                    f"Failed to generate api parameters for {operation_markup}. Error: {generation_error}"
                )
                inform_about_develeoping_custom_resource_nodes()
                return False, generation_error
            if isinstance(generated_api_parameters, Iterable):
                logger.debug(
                    f"Successfuly generated api parameters for {operation_markup}, count: {len(generated_api_parameters)}"
                )
                # filter generated_api_parameters if a pattern option is provided
                api_parameters_for_operation = generated_api_parameters
                if match_patterns:
                    pattern_matched_api_parameters = api_parameters_match_pattern(
                        generated_api_parameters, match_patterns
                    )
                    logger.debug(
                        f"Matching patterns: {match_patterns}. Filtered the generated api parameters [{len(pattern_matched_api_parameters)}/{len(generated_api_parameters)}]"
                    )
                    api_parameters_for_operation = pattern_matched_api_parameters
                for api_parameter in api_parameters_for_operation:
                    # for each parameter generated, call the actual operation
                    self.call_operation(resource_node, operation_name, api_parameter, follow_pagination=follow_pagination)
            # after calling the same operation for the different parameters
            # get all the response data made for this operation_name
            logger.debug(f"[underline][bold]Done Reading[/] {operation_markup}[/]")
            return self.search_operation_data(resource_node_name, operation_name)

        # OPERATION HAVE RELATIONS
        all_related_operations_data = {}

        # for each relation, fetch the related resource's data.
        for rel in relations_of_operation:
            rel_operation_data = self.read_operation(
                rel.resource_node_name, rel.operation_name, refresh=refresh, follow_pagination=follow_pagination
            )
            if not rel_operation_data:
                logger.debug(
                    f"[red]Failed to read related operation[/]: {rel.resource_node_name}.{rel.operation_name}"
                )
                inform_about_develeoping_custom_resource_nodes()
                return False

            # gather all their related operations data, put it under a dict
            all_related_operations_data.update({rel.operation_name: rel_operation_data})

        # send the operations_data to resource_node to create valid_api_parameters
        (
            generated_api_parameters,
            generation_error,
        ) = resource_node.generate_api_parameters_from_operation_data(
            operation_name, relations_of_operation, all_related_operations_data
        )
        
        if generated_api_parameters == [] and generation_error is None:
            # no errors, just no data available to generate api parameters
            logger.debug(
                f"[bold yellow]WARNING: There's no related resource data in your account to generate the api params for: {operation_markup}."
            )
        
        if generation_error is not None:
            logger.debug(
                f"Failed to generate api parameters for {operation_markup}: {generation_error}"
            )
            inform_about_develeoping_custom_resource_nodes()

            return False
        elif isinstance(generated_api_parameters, Iterable):
            logger.debug(
                f"Successfuly generated api parameters for [bold blue]{operation_name}[/], count: {len(generated_api_parameters)}"
            )
            # filter generated_api_parameters if a pattern option is provided
            api_parameters_for_operation = generated_api_parameters
            if match_patterns:
                pattern_matched_api_parameters = api_parameters_match_pattern(
                    generated_api_parameters, match_patterns
                )
                logger.debug(
                    f"Matching given patterns: {match_patterns}. Filtered the generated api parameters [{len(pattern_matched_api_parameters)}/{len(generated_api_parameters)}]"
                )
                api_parameters_for_operation = pattern_matched_api_parameters
            for api_parameter in api_parameters_for_operation:
                # for each parameter generated, call the actual operation
                self.call_operation(resource_node, operation_name, api_parameter, follow_pagination=follow_pagination)
        else:
            logger.debug(f"Failed to generate api parameters for {operation_markup}")

        # after calling the same operation for the different parameters
        # get all the response data made for this operation_name
        logger.debug(f"[underline][bold]Done Reading[/] {operation_markup}[/]")

        return self.search_operation_data(resource_node_name, operation_name)

    def read_resource_node(
        self,
        resource_node_name: str,
        match_patterns: Optional[List[str]] = None,
        refresh: Optional[bool] = False,
        follow_pagination: Optional[bool] = False,
    ) -> Union[Dict, bool]:
        """Reads all available operations in the given a resource node

        Args:
            resource_node_name (str): _description_
            match_patterns (List[str], optional): UNIX style patterns to filter the generated parameters. Defaults to None.
            refresh (Optional[bool], optional): Use the cached data or always make new calls. Defaults to False.
            follow_pagination (Optional[bool], optional): Follow pagination if the output is truncated.. Defaults to False.

        Returns:
            Union[Dict, bool]: Data read if successful, or False.
        """

        resource_node = self.service_node.get_resource_node_by_name(resource_node_name)
        if not resource_node:
            return False

        for operation_name in resource_node.operation_names:
            self.read_operation(
                resource_node_name, operation_name, match_patterns, refresh=refresh, follow_pagination=follow_pagination
            )
        return self.search_resource_node_data(resource_node.name)
