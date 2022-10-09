"""
Any resource that app system is going to use must be exported here.
Otherwise different import statements would create new global static objects
for AppRegistry etc.
"""
from registries import app_registry, AppRegistry
from app import BaseBalconyApp
from factories import BalconyAWS