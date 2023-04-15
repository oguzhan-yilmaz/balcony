from config import get_logger, get_rich_console
from yaml_config import find_and_parse_yaml_services
from typing import Dict, Union

console = get_rich_console()
logger = get_logger(__name__)


class ResourceNodeRegistry:
    _registry = {}
    _yaml_config_registry = {}

    def __init__(self) -> None:
        yaml_services = find_and_parse_yaml_services()
        for yaml_service in yaml_services:
            service_name = yaml_service.service_name
            if service_name not in self._yaml_config_registry:
                self._yaml_config_registry[service_name] = {}

            for yaml_r_node_config in yaml_service.resource_nodes:
                rn_name = yaml_r_node_config.resource_node_name
                self._yaml_config_registry[service_name][rn_name] = yaml_r_node_config
                logger.debug(f"YamlRegistry: Registered {service_name}.{rn_name}")

    def search_yaml_config_registry(self, service_name, resource_node_name):
        return self._yaml_config_registry.get(service_name, {}).get(
            resource_node_name, None
        )

    def register_class(
        self, cls: "ResourceNode", service_name: str = None, name: str = None
    ) -> None:
        """Register a subclass of ResourceNode with the given `service_name` and `name`.
        When a ResourceNode object is created, registered classes will be selected as the
        ResourceNode class. This allows overriding ability to each service/resource.

        Args:
            cls (ResourceNode): A subclass of ResourceNode
            service_name (str, optional): ServiceNode name, must be provided. Defaults to None.
            name (str, optional): ResourceNode name, must be provided. Defaults to None.


        """
        # TODO: check if service_name is correct get_available_service_names
        service_dict = self._registry.get(service_name, False)
        if not service_dict:
            self._registry[service_name] = {name: cls}
        else:
            custom_resource_node = service_dict.get(name, False)
            if custom_resource_node:
                return False
            else:
                self._registry[service_name][name] = cls

    def search_registry_for_service(
        cls, service_name: str
    ) -> Dict[str, "ResourceNode"]:
        """Returns services registered custom ResourceNode subclasses.

        Returns:
            Dict[str, 'ResourceNode']: ResourceNode name to custom Subclasses mapping for the service.
        """
        return cls._registry.get(service_name, {})

    def find_custom_class_for_resource_node(
        cls, service_name: str, node_name: str
    ) -> Union["ResourceNode", bool]:
        """Try to find the ResourceNode's custom subclasses registered under the Service.

        Returns:
            Union["ResourceNode", bool] : False if no custom class is found, else the custom class
        """
        services_custom_nodes = cls.search_registry_for_service(service_name)
        for custom_cls_name, _cls_obj in services_custom_nodes.items():
            # if compare_two_camel_case_words(custom_cls_name, node_name):
            if custom_cls_name.lower() == node_name.lower():
                return _cls_obj

        return False
