import os
from importlib import import_module
class ImproperlyConfigured(Exception): pass
import sys
APPS_MODULE_NAME = 'app'
import sys
from importlib.util import find_spec as importlib_find

class AppRegistry:
    _registry = {}
    
    def __init__(self) -> None:
        print('AppRegistry initialized', hash(id(self)))
   
    def get_registered_apps(self):
       return self._registry
   
    def register_app_class(self, cls, author=None, app_name=None, description=None, tags=(), **kwargs):
        app_dict = {
            'app_name': app_name,
            'cls': cls,
            'description': description,
            'tags': tags,
            'kwargs': kwargs
        }
        author_dict = self._registry.get(author, False)
        if not author_dict:
            self._registry[author] = [app_dict]
        else:
            # TODO: check if same name exists
            self._registry[author].append(app_dict)

    @staticmethod
    def import_balcony_apps(insalled_apps=None):
        for entry in insalled_apps:
            # import the entry
            try:
                print(f'importing {entry}')
                app_module = import_module(entry)
                app_module
            except Exception as e:
                pass
            else:
                if module_has_submodule(app_module, APPS_MODULE_NAME):
                    mod_path = "%s.%s" % (entry, APPS_MODULE_NAME)
                    mod = import_module(mod_path)
                    mod
    # TODO: save the module info and return it
    
app_registry = AppRegistry()
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
    
    
    

def cached_import(module_path, class_name):
    # Check whether module is loaded and fully initialized.
    if not (
        (module := sys.modules.get(module_path))
        and (spec := getattr(module, "__spec__", None))
        and getattr(spec, "_initializing", False) is False
    ):
        module = import_module(module_path)
    return getattr(module, class_name)


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit(".", 1)
    except ValueError as err:
        raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    try:
        return cached_import(module_path, class_name)
    except AttributeError as err:
        raise ImportError(
            'Module "%s" does not define a "%s" attribute/class'
            % (module_path, class_name)
        ) from err


def autodiscover_modules(*args, **kwargs):
    """
    Auto-discover INSTALLED_APPS modules and fail silently when
    not present. This forces an import on them to register any admin bits they
    may want.

    You may provide a register_to keyword parameter as a way to access a
    registry. This register_to object must have a _registry instance variable
    to access it.
    """

    # TODO static init
    register_to = kwargs.get("register_to")
    for app_config in app_registry.get_app_configs():
        for module_to_search in args:
            # Attempt to import the app's module.
            try:
                if register_to:
                    before_import_registry = copy.copy(register_to._registry)

                import_module("%s.%s" % (app_config.name, module_to_search))
            except Exception:
                # Reset the registry to the state before the last import
                # as this import will have to reoccur on the next request and
                # this could raise NotRegistered and AlreadyRegistered
                # exceptions (see #8245).
                if register_to:
                    register_to._registry = before_import_registry

                # Decide whether to bubble up this error. If the app just
                # doesn't have the module in question, we can ignore the error
                # attempting to import it, otherwise we want it to bubble up.
                if module_has_submodule(app_config.module, module_to_search):
                    raise


def module_has_submodule(package, module_name):
    """See if 'module' is in 'package'."""
    try:
        package_name = package.__name__
        package_path = package.__path__
    except AttributeError:
        # package isn't a package.
        return False

    full_module_name = package_name + "." + module_name
    try:
        return importlib_find(full_module_name, package_path) is not None
    except ModuleNotFoundError:
        # When module_name is an invalid dotted path, Python raises
        # ModuleNotFoundError.
        return False


def module_dir(module):
    """
    Find the name of the directory that contains a module, if possible.

    Raise ValueError otherwise, e.g. for namespace packages that are split
    over several directories.
    """
    # Convert to list because __path__ may not support indexing.
    paths = list(getattr(module, "__path__", []))
    if len(paths) == 1:
        return paths[0]
    else:
        filename = getattr(module, "__file__", None)
        if filename is not None:
            return os.path.dirname(filename)
    raise ValueError("Cannot determine directory containing %s" % module)
