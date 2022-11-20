import boto3
try:
    from .utils import get_all_available_services, _create_boto_session
    from .nodes import ServiceNode
    from .reader import ServiceReader
except ImportError:
    from utils import get_all_available_services, _create_boto_session
    from nodes import ServiceNode
    from reader import ServiceReader

from typing import Optional, List, Dict, Tuple

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
    def __init__(self, boto3_session: boto3.session.Session):
        self.boto3_session = boto3_session
        self._service_nodes_map = {}

    def _create_service_node(self, service_name:str) -> None:
        service_node = ServiceNode(service_name, self.boto3_session)
        self._service_nodes_map[service_name] = service_node

    def get_service_node(self, service_name:str) -> ServiceNode:
        if not service_name in self._service_nodes_map:
            self._create_service_node(service_name)            
        return self._service_nodes_map.get(service_name)
    
    def get_service_reader(self, service_name:str) -> ServiceReader:
        service_node = self.get_service_node(service_name)
        if service_node:
            return service_node.get_service_reader()

    def read_operation(self, service_name:str, resource_node_name:str, operation_name:str, 
                       match_patterns:Optional[List[str]]=None, refresh:Optional[bool]=False):    
        service_reader = self.get_service_reader(service_name)
        if service_reader:
            data = service_reader.read_operation(resource_node_name, operation_name, match_patterns, refresh)
            return data
        return False
    
    def get_available_service_node_names(self) -> List[str]:
        return get_all_available_services(self.boto3_session)
    
    
