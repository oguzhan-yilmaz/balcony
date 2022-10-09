import boto3
try:
    from .utils import get_all_available_services, _create_boto_session
    from .nodes import ServiceNode
    from .factories import Boto3SessionSingleton, BalconyAWS, balcony_client

except ImportError:
    from utils import get_all_available_services, _create_boto_session
    from nodes import ServiceNode
    
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
    def __init__(self, boto3_session):
        self.boto3_session = boto3_session
        self._service_nodes_map = {}

    def _create_service_node(self, service_name):
        service_node = ServiceNode(service_name, self.boto3_session)
        self._service_nodes_map[service_name] = service_node

    def get_service_node(self, service_name):
        if not service_name in self._service_nodes_map:
            self._create_service_node(service_name)            
        return self._service_nodes_map.get(service_name)
    





class BalconyAWS:
    def __init__(self, boto3_session=None) -> None:
        if boto3_session is None:
            self.boto3_session = Boto3SessionSingleton().get_session()
        else:
            self.boto3_session = boto3_session
        self.service_node_factory = ServiceNodeFactory(self.boto3_session)
        
    def get_available_service_node_names(self):
        return get_all_available_services(self.boto3_session)
    
    
    def get_service(self, service_name:str) -> ServiceNode:
        service_node = self.service_node_factory.get_service_node(service_name)
        return service_node
    

