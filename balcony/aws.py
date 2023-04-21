from utils import get_all_available_services, _create_boto_session
from nodes import ServiceNode
from reader import ServiceReader

from typing import Optional, List, Union
import boto3


class BalconyAWS:
    """Provides a concise interface for using balcony's functionalities.

    It can be used to reading AWS Operations, or accessing underlying
    ServiceNodes and ServiceReaders.

    ```python title="Creating a BalconyAWS obj and reading IAM Roles"
    baws = BalconyAWS()
    roles = baws.read_resource_node('iam', 'Role', follow_pagination=True)
    print(roles)
    ```
    """

    def __init__(self, boto3_session: Optional[boto3.session.Session] = None):
        """Initializes this object with an optional `boto3.session.Session` object.
        If it's not provided, default boto3 session is created from the shell credentials.

        Args:
            boto3_session (Optional[boto3.session.Session], optional): Custom boto3 Session object. If not given,
                                                                        default Session will be used.
        """
        self.boto3_session = boto3_session
        if boto3_session is None:
            self.boto3_session = _create_boto_session()

        # Stores the created ServiceNodes by their names
        self._service_nodes_map = {}

    def _create_service_node(self, service_name: str) -> None:
        """Creates the ServiceNode with the `self.boto3_session`

        Args:
            service_name (str): Name of the AWS Service
        """
        service_node = ServiceNode(service_name, self.boto3_session)
        self._service_nodes_map[service_name] = service_node

    def get_service_node(self, service_name: str) -> ServiceNode:
        """Gets or creates the ServiceNode.

        Args:
            service_name (str): Name of the AWS Service.

        Returns:
            ServiceNode: ServiceNode object representing an AWS Service
        """
        if service_name not in self._service_nodes_map:
            self._create_service_node(service_name)
        return self._service_nodes_map.get(service_name)

    def get_service_reader(self, service_name: str) -> ServiceReader:
        """Gets the ServiceReader obj from the ServiceNode obj.

        Args:
            service_name (str): Name of the AWS Service.

        Returns:
            ServiceReader: ServiceReader object with the read capabilities, tied to a ServiceNode.
        """
        service_node = self.get_service_node(service_name)
        if service_node:
            return service_node.get_service_reader()

    def read_operation(
        self,
        service_name: str,
        resource_node_name: str,
        operation_name: str,
        match_patterns: Optional[List[str]] = None,
        refresh: Optional[bool] = False,
        follow_pagination: Optional[bool] = False,
    ) -> Union[dict, bool]:
        """Call the AWS API operation for the given `service_name`, `resource_node_name` and `operation_name` values.

        Args:
            service_name (str): AWS Service name.
            resource_node_name (str): AWS ResourceNode name
            operation_name (str): AWS Read opeartion name
            match_patterns (Optional[List[str]], optional): UNIX style patterns for generated required_parameters. Defaults to None.
            refresh (Optional[bool], optional): Force to re-read instead of returning the data from cache.. Defaults to False.
            follow_pagination (bool, optional): Follow pagination tokens. If not only set True, one page call will be made.

        Returns:
            Union[dict,bool]: Read Operation data, or False.
        """
        service_reader = self.get_service_reader(service_name)
        if service_reader:
            data = service_reader.read_operation(
                resource_node_name,
                operation_name,
                match_patterns,
                refresh,
                follow_pagination=follow_pagination,
            )
            return data
        return False

    def read_resource_node(
        self,
        service_name: str,
        resource_node_name: str,
        match_patterns: Optional[List[str]] = None,
        refresh: Optional[bool] = False,
        follow_pagination: Optional[bool] = False,
    ) -> Union[dict, bool]:
        """Reads all available Read operations of the given ResourceNode.

        Args:
            service_name (str): Name of the AWS Service
            resource_node_name (str): Name of the AWS Resource Node
            match_patterns (Optional[List[str]], optional): UNIX style patterns for generated required_parameters. Defaults to None.
            refresh (bool, optional): Force to re-read instead of returning the data from cache.. Defaults to False.
            follow_pagination (bool, optional): Follow the pagination tokens if the output is truncated. Defaults to False.

        Returns:
            Union[dict,bool]: Read ResourceNode data or False
        """
        service_reader = self.get_service_reader(service_name)
        if service_reader:
            data = service_reader.read_resource_node(
                resource_node_name,
                match_patterns,
                refresh=refresh,
                follow_pagination=follow_pagination,
            )
            return data
        return False

    def get_available_service_names(self) -> List[str]:
        """Lists available AWS service namese

        Returns:
            List[str]: Available service names for current `boto3.session.Session`
        """
        return get_all_available_services(self.boto3_session)
