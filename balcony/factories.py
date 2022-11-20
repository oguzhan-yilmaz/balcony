import boto3
try:
    from .utils import get_all_available_services, _create_boto_session
    from .nodes import ServiceNode
    from .reader import ServiceReader
except ImportError:
    from utils import get_all_available_services, _create_boto_session
    from nodes import ServiceNode
    from reader import ServiceReader

from typing import Optional, List, Dict, Tuple, Union

class Boto3SessionSingleton(object):
    _instance = None
    _session = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Boto3SessionSingleton, cls).__new__(cls)
            # Put any initialization here.
            # cls._session = _create_boto_session()
        return cls._instance


    def __init__(self):
        if not self._session:
            self._session = _create_boto_session()
    
    def get_session(self):
        return self._session

class ServiceNodeFactory:
    """Represents the whole AWS API.
    Can be used to get ServiceNodes and ServiceReaders.
    Operations can be read with `read_` functions.
    
    ```python title="Creating a ServiceNodeFactory and reading IAM Roles"
    service_factory = ServiceNodeFactory()
    roles = service_factory.read_resource_node('iam', 'Role')
    print(roles)
    ```
    
    """
    def __init__(self, boto3_session: Optional[boto3.session.Session]=None):
        self.boto3_session = boto3_session
        if boto3_session is None:
            self.boto3_session = _create_boto_session()
        self._service_nodes_map = {}

    def _create_service_node(self, service_name:str) -> None:
        """Creates the ServiceNode w/ the `self.boto3_session`. 

        Args:
            service_name (str): Name of the AWS Service
        """
        service_node = ServiceNode(service_name, self.boto3_session)
        self._service_nodes_map[service_name] = service_node

    def get_service_node(self, service_name:str) -> ServiceNode:
        """Gets or creates the ServiceNode.

        Args:
            service_name (str): Name of the AWS Service.

        Returns:
            ServiceNode: ServiceNode object representing an AWS Service. 
        """
        if not service_name in self._service_nodes_map:
            self._create_service_node(service_name)            
        return self._service_nodes_map.get(service_name)
    
    def get_service_reader(self, service_name:str) -> ServiceReader:
        """Gets the ServiceReader obj from the ServiceNode obj.

        Args:
            service_name (str): Name of the AWS Service.

        Returns:
            ServiceReader: ServiceReader object with the read capabilities, tied to a ServiceNode.
        """
        service_node = self.get_service_node(service_name)
        if service_node:
            return service_node.get_service_reader()

    def read_operation(self, service_name:str, resource_node_name:str, operation_name:str, 
                       match_patterns:Optional[List[str]]=None, refresh:Optional[bool]=False) -> Union[dict,bool]:    
        """Call the AWS API operation for the given `service_name`, `resource_node_name` and `operation_name` values.
        

        Args:
            service_name (str): AWS Service name.
            resource_node_name (str): AWS ResourceNode name
            operation_name (str): AWS Read opeartion name
            match_patterns (Optional[List[str]], optional): UNIX style patterns for generated required_parameters. Defaults to None.
            refresh (Optional[bool], optional): Force to re-read instead of returning the data from cache.. Defaults to False.

        Returns:
            Union[dict,bool]: Read Operation data, or False. 
        """
        service_reader = self.get_service_reader(service_name)
        if service_reader:
            data = service_reader.read_operation(resource_node_name, operation_name, match_patterns, refresh)
            return data
        return False
    
    def read_resource_node(self, service_name:str, resource_node_name:str, 
                           match_patterns:Optional[List[str]]=None, refresh:Optional[bool]=False) -> Union[dict,bool]:
        """Reads all available Read operations of the given ResourceNode.

        Args:
            service_name (str): Name of the AWS Service
            resource_node_name (str): Name of the AWS Resource Node
            match_patterns (Optional[List[str]], optional): UNIX style patterns for generated required_parameters. Defaults to None.
            refresh (Optional[bool], optional): Force to re-read instead of returning the data from cache.. Defaults to False.

        Returns:
            Union[dict,bool]: Read ResourceNode data or False
        """
        service_reader = self.get_service_reader(service_name)
        if service_reader:
            data = service_reader.read_resource_node(resource_node_name, match_patterns, refresh)
            return data
        return False
    
    def get_available_service_node_names(self) -> List[str]:
        """Lists available AWS service names. 

        Returns:
            List[str]: Available service names for current `boto3.session.Session`
        """
        return get_all_available_services(self.boto3_session)
    
    
