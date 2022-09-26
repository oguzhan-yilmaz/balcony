try:
    from .utils import compare_two_camel_case_words
except ImportError:
    from utils import compare_two_camel_case_words
class ResourceNodeRegistry:
    _registry = {}

    def __init_subclass__(cls, service_name=None, name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        # TODO: check if service_name is correct get_available_service_names
        service_dict = cls._registry.get(service_name, False)
        if not service_dict:
            cls._registry[service_name] = {name: cls}
        else:
            custom_resource_node = service_dict.get(name, False)
            if custom_resource_node:
                raise Exception(
                    f"A custom ResourceNode is already registered with Service: {service_name}, Resource Node: {name}. Duplication is not allowed.")
            else:
                cls._registry[service_name][name] = cls

    def _search_registry_for_service(cls, service_name):
        return cls._registry.get(service_name, {})

    def find_custom_class_for_resource_node(cls, service_name, node_name):
        services_custom_nodes = cls._search_registry_for_service(service_name)
        for custom_cls_name, _cls_obj in services_custom_nodes.items():
            # if compare_two_camel_case_words(custom_cls_name, node_name):
            if custom_cls_name.lower() == node_name.lower():
                return _cls_obj
        return False