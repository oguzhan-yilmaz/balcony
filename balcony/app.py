from pprint import pprint
from typing import Union
import sys
from importlib import import_module
from typer.models import TyperInfo
from typer.main import Typer
try:
    from .registries import app_registry
except ImportError:
    from registries import app_registry

APPS_MODULE_NAME = "app"

class BaseBalconyApp:
    author = None
    app_name = None
    description = None
    tags = ()
    
    def __init_subclass__(cls, author=None, app_name=None, description=None, tags=(), **kwargs):
        super().__init_subclass__(**kwargs)
        cls.author = author
        cls.app_name = app_name
        cls.description =description
        cls.tags = tags
        app_registry.register_app_class(cls, author, app_name, description, tags, **kwargs)

        

            
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        print('BaseBalconyApp initialized.')
        # self.name = name
        

    def get_data(self, *args, **kwargs) -> dict:
        """"""
        raise NotImplementedError("Please Implement this method")
    
    def get_cli_app(self, *args, **kwargs) -> Typer:
        """"""
        # TODO: create default cli app on template repository
        raise NotImplementedError("Please Implement this method")
        
# class BaseBalconyAppResource:
#     def __init__(self, name, *args, **kwargs) -> None:
#         self.name = name

"""
balcony-app/
    


"""