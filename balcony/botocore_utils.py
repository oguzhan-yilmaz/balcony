from functools import lru_cache
from typing import List, Union
from botocore.model import Shape, DenormalizedStructureBuilder, OperationModel

try:
    from .utils import icompare_two_camel_case_words
    from .logs import get_rich_console
except ImportError:
    from utils import icompare_two_camel_case_words
    from logs import get_rich_console



from collections import namedtuple
from rich.text import Text
from rich.tree import Tree
from rich.layout import Layout
ShapeAndTargetPath = namedtuple('ShapeAndTargetPath', ['shape', 'target_path'])

UNWANTED_SHAPE_NAMES = ('String', 'DateTime', 'Name', 'Id', 'Arn', '__string')
UNWANTED_SHAPE_NAMES_LOWERED = [_.lower() for _ in UNWANTED_SHAPE_NAMES]
SHAPE_SCALAR_TYPES = DenormalizedStructureBuilder.SCALAR_TYPES
SHAPE_COLLECTION_TYPES = ('structure', 'list','map')
READ_ONLY_VERBS = ('Describe', 'List', 'Get')
IDENTIFIER_NAMES = ('arn', 'id', 'name', 'arns', 'ids',
                    'names', 'identifier', 'identifiers', 'number', 'url')
BLACKLISTED_SHAPE_NAMES = ('ComponentChildList','FirewallManagerRuleGroups', 'Rules','HeaderNames', 'ExcludedRules', 'CountryCodes', 'CookieNames', 'TextTransformations', 'ComponentSummaryList','AnomalyMonitors','ConfigurationList','HandshakeResources','JsonPointerPaths','AdministrativeActions','DataValueList','ThemeValuesList','Expressions','CostCategoryRulesList')

console = get_rich_console()

def find_key_in_dict_keys(key:str, dict_keys: Union[list, dict]) -> str:
    """Case insensitive search for a `key` in a `list` or `dict.keys()`. 

    Args:
        key (str): Search case insensively for
        dict_keys (Union[list, dict]): In a list or keys of dictionary

    Returns:
        str: Found key that case insensively matches the given key.
    """
    dict_keys_list = dict_keys
    if type(dict_keys) == dict:
        dict_keys_list = dict_keys.keys()
    for dict_key in dict_keys_list:
        if key.lower() == dict_key.lower():
            return dict_key
    return False

def ifind_key_in_dict_keys(key:str, dict_keys: Union[list, dict]) -> str:
    """Case insensitive search for a `key` in a `list` or `dict.keys()`. 

    Args:
        key (str): Search case insensively for
        dict_keys (Union[list, dict]): In a list or keys of dictionary

    Returns:
        str: Found key that case insensively matches the given key.
    """
    dict_keys_list = dict_keys
    if type(dict_keys) == dict:
        dict_keys_list = dict_keys.keys()
    for dict_key in dict_keys_list:
        if icompare_two_camel_case_words(key, dict_key):
            return dict_key
    return False

def get_max_results_value_from_shape(input_shape: Shape) -> int:
    """Finds the `MaxResults` highest value for an input shape.

    Args:
        input_shape (Shape): Input shape of an operation. Generally postfixed with `Request`.

    Returns:
        int: `MaxResults` highest value if found in the Shape definition
    """
    flat_shapes_and_target_paths = flatten_shape_to_its_non_collection_shape_and_target_paths(input_shape)
    flat_members = [_.shape for _ in flat_shapes_and_target_paths]
    result = False
    for member_shape in flat_members:
        shape_key_name = getattr(member_shape, 'key_name', False)
        is_key_name_maxresults = shape_key_name and (shape_key_name.lower() == 'maxresults')
        shape_name = get_shape_name(member_shape)
        if shape_name.lower() == 'maxresults' or is_key_name_maxresults:
            member_shape
            max_value = member_shape.metadata.get('max', False)
            if max_value:
                return max_value
    return False

def get_input_shape(operation_model: OperationModel) -> Shape:
    """Get the input shape of the operation model

    Args:
        operation_model (OperationModel): botocore OperationModel 

    Returns:
        Shape: Input Shape of the OperationModel
    """
    return getattr(operation_model, 'input_shape', False)



def get_members_shapes(shape: Shape) -> List[Shape]:
    """Get the member shapes of and input or output Shape.

    Args:
        shape (Shape): Shape to get members from

    Returns:
        List[Shape]: Member Shapes, added `key_name` and `parent_name` values to objects.
    """
    found_members_shapes = []
    if not shape:
        return found_members_shapes
    if shape.name in BLACKLISTED_SHAPE_NAMES:
        return found_members_shapes
    if shape.type_name == 'structure':
        for shape_key, member in shape.members.items():
            setattr(member, 'key_name', shape_key)
            setattr(member, 'parent_name', shape.name)
            found_members_shapes.append(member)
    elif shape.type_name == 'list':
        only_member = shape.member
        found_members_shapes.append(only_member)
    elif shape.type_name == 'map':
        t = get_members_shapes(shape.value)
        return t
    return found_members_shapes


def filter_non_collection_shape(shape_and_target_path: ShapeAndTargetPath) -> bool:
    """Bool function to check ShapeAndTargetPath Named Tuple 

    Args:
        shape_and_target_path (ShapeAndTargetPath): Named Tuple. 

    Returns:
        bool: _description_
    """
    shape = shape_and_target_path.shape
    has_key_name = getattr(shape, 'key_name', False)
    is_non_collection = shape.type_name not in SHAPE_COLLECTION_TYPES
    return has_key_name and is_non_collection


def _flatten_shape_to_its_members_and_target_paths(shape, target_str='', ):
    result = []
    members = get_members_shapes(shape)
    for member in members:
        member_key_name = getattr(member, 'key_name', False)
        new_target_str = target_str
        if member_key_name:
            if target_str == '':
                new_target_str = f"{member_key_name}"
            else:
                new_target_str = f"{target_str}[*].{member_key_name}"
        if member.type_name in ('structure', 'list'):# TODO:SHAPE_COLLECTION_TYPES-('map',):
            inner_list = _flatten_shape_to_its_members_and_target_paths(member, new_target_str)
            result.extend(inner_list)
        else:
            result.append(ShapeAndTargetPath(member, new_target_str))
    return result

def flatten_shape_to_its_non_collection_shape_and_target_paths(shape):
    all_flat_members_and_target_paths = _flatten_shape_to_its_members_and_target_paths(shape)
    non_collection_shapes_and_target_paths = list(filter(filter_non_collection_shape, all_flat_members_and_target_paths))
    return non_collection_shapes_and_target_paths

"""
    root = Tree("🌲 [b green]Rich Tree", highlight=True, hide_root=True)
    node = root.add(":file_folder: Renderables", guide_style="red")
    simple_node = node.add(":file_folder: [bold yellow]Atomic", guide_style="uu green")
    simple_node.add(Group("📄 Syntax", syntax))
    simple_node.add(Group("📄 Markdown", Panel(markdown, border_style="green")))
    containers_node = node.add(
        ":file_folder: [bold magenta]Containers", guide_style="bold magenta"
    )
    containers_node.expanded = True
    panel = Panel.fit("Just a panel", border_style="red")
    containers_node.add(Group("📄 Panels", panel))

therewillbebeloodthere
        containers_node.add(Group("📄 [b magenta]Table", table))

    console = Console()

    console.print(root)
"""


def rich_str_shape(shape: Shape) -> str:
    """Transforms a Shape to rich supported string.

    Args:
        shape (Shape): botocore.model.Shape object.

    Returns:
        str: Rich string for shape.
    """
    key_name = getattr(shape, 'key_name', '{')
    type_name = str(shape.type_name)
    if key_name == '{' and type_name == 'structure':
        type_name = ''
    if type_name:
        type_name = f"({type_name})"
    shape_str = f"[blue]{key_name} [white]{type_name}"
    return shape_str


def generate_rich_tree_from_shape(shape: Shape) -> Tree:
    """Genereate a rich Tree containing `shape` and it's members."""
    tree = Tree(rich_str_shape(shape), guide_style="red")
    def _recursive_stringify_shape(shape, node):

        members = get_members_shapes(shape)
        for member in members:
            member_str = rich_str_shape(member) 
            if member.type_name in SHAPE_COLLECTION_TYPES:
                new_node = node.add(member_str)
                _recursive_stringify_shape(member, new_node)
            else:
                node.add(member_str)
    _recursive_stringify_shape(shape, tree)
    return tree
        
    
# @lru_cache(maxsize=500) # print(get_shape_name.cache_info())
def get_shape_name(shape: Shape) -> str:
    """Returns the shapes name, using custom set object values"""
    shape_name = shape.name
    shape_key_name = getattr(shape, 'key_name', False)
    if shape_name.lower() in UNWANTED_SHAPE_NAMES_LOWERED:
        # check for name forgotten in shape.serialization if the name is a type name.
        if shape_key_name:
            return shape_key_name
        elif shape.serialization and shape.serialization.get('name', False):
            given_serialization_name = shape.serialization.get('name')
            return given_serialization_name
    return shape_name
   
def get_required_parameter_shapes_from_operation_model(operation_model: OperationModel) -> List[Shape]:
    input_shape = get_input_shape(operation_model)
    if not input_shape:
        return [] # there's no input shape
    input_shape_members = get_members_shapes(input_shape)
    input_required_member_names = input_shape.required_members
    if input_required_member_names == []:
        return []
    
    required_member_shapes = []
    for input_member in input_shape_members:
        input_member_name = get_shape_name(input_member)
        for required_name in input_required_member_names:
            if icompare_two_camel_case_words(required_name, input_member_name):
                required_member_shapes.append(input_member)
            
    return required_member_shapes

# def get_required_parameters_for_operation(operation_model):
#     required_parameter_shapes = get_required_parameters_for_operation(operation_model)
#     required_parameter_names = [
#         get_shape_name(r_param_shape)
#         for r_param_shape in required_parameter_shapes
#     ]
#     return required_parameter_names

def compare_shape_names(member, search_shape):
    return get_shape_name(member) == get_shape_name(search_shape)


