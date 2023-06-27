from utils import icompare_two_camel_case_words
from config import get_rich_console

from typing import List, Union
from botocore.model import Shape, DenormalizedStructureBuilder, OperationModel
from rich.markup import escape
import re
from collections import namedtuple
from rich.tree import Tree

ShapeAndTargetPath = namedtuple("ShapeAndTargetPath", ["shape", "target_path"])

UNWANTED_SHAPE_NAMES = ("String", "DateTime", "Name", "Id", "Arn", "__string")
UNWANTED_SHAPE_NAMES_LOWERED = [_.lower() for _ in UNWANTED_SHAPE_NAMES]
SHAPE_SCALAR_TYPES = DenormalizedStructureBuilder.SCALAR_TYPES
_MAX_ALLOWED_RECURSION = 10
SHAPE_COLLECTION_TYPES = ("structure", "list", "map")
READ_ONLY_VERBS = ("Describe", "List", "Get")
IDENTIFIER_NAMES = (
    "arn",
    "id",
    "name",
    "arns",
    "ids",
    "names",
    "identifier",
    "identifiers",
    "number",
    "url",
)

# shape_resolver can't find the reference of BLACKLISTED_SHAPE_NAMES, so they're ignored
BLACKLISTED_SHAPE_NAMES = (
    "ComponentChildList",
    "FirewallManagerRuleGroups",
    "Rules",
    "HeaderNames",  # noqa
    "ExcludedRules",
    "CountryCodes",
    "CookieNames",
    "TextTransformations",
    "ComponentSummaryList",  # noqa
    "AnomalyMonitors",
    "ConfigurationList",
    "HandshakeResources",
    "JsonPointerPaths",  # noqa
    "AdministrativeActions",
    "DataValueList",
    "ThemeValuesList",
    "Expression",
    "Expressions",
    "CostCategoryRulesList",
    "GetCostAndUsageRequest",
    "GetCostAndUsageWithResourcesRequest",
    "GetAnomaliesRequest",
    "InventoryAggregator",
    "OpsFilter",
    "OpsAggregator",
    "QueryStagePlanNodes",
    "QueryStagePlanNode",
    "QueryStage",
    "ElicitSubSlot",
    "DialogAction",
)  # noqa
# regex expr for removing html caret tags
HTML_CLEANER_REGEX = re.compile("<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")

console = get_rich_console()


def find_key_in_dict_keys(key: str, dict_keys: Union[list, dict]) -> str:
    """Case insensitive search for a `key` in a `list` or `dict.keys()`.
    Returns the existing key.

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


def ifind_key_in_dict_keys(key: str, dict_keys: Union[list, dict]) -> str:
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
    flat_shapes_and_target_paths = (
        flatten_shape_to_its_non_collection_shape_and_target_paths(input_shape)
    )
    flat_members = [_.shape for _ in flat_shapes_and_target_paths]
    for member_shape in flat_members:
        shape_key_name = getattr(member_shape, "key_name", False)
        is_key_name_maxresults = shape_key_name and (
            shape_key_name.lower() == "maxresults"
        )
        shape_name = get_shape_name(member_shape)
        if shape_name.lower() == "maxresults" or is_key_name_maxresults:
            member_shape
            max_value = member_shape.metadata.get("max", False)
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
    return getattr(operation_model, "input_shape", False)


def get_members_shapes(shape: Shape, _recursion_count=0) -> List[Shape]:
    """Get the member shapes of and input or output Shape.

    Args:
        shape (Shape): Shape to get members from

    Returns:
        List[Shape]: Member Shapes, added `key_name` and `parent_name` values to objects.
    """

    found_members_shapes = []

    if _recursion_count >= _MAX_ALLOWED_RECURSION:
        return found_members_shapes

    if not shape:
        return found_members_shapes
    if shape.name in BLACKLISTED_SHAPE_NAMES:
        return found_members_shapes

    if shape.type_name == "structure":
        for shape_key, member in shape.members.items():
            setattr(member, "key_name", shape_key)
            setattr(member, "parent_name", shape.name)
            found_members_shapes.append(member)
    elif shape.type_name == "list":
        only_member = shape.member
        found_members_shapes.append(only_member)
    elif shape.type_name == "map":
        t = get_members_shapes(shape.value, _recursion_count + 1)
        return t
    return found_members_shapes


def is_shape_non_collection_type(shape_and_target_path: ShapeAndTargetPath) -> bool:
    """Boolean function to check ShapeAndTargetPath Named Tuple

    Args:
        shape_and_target_path (ShapeAndTargetPath): Named Tuple

    Returns:
        bool: _description_
    """
    shape = shape_and_target_path.shape
    has_key_name = getattr(shape, "key_name", False)
    is_non_collection = shape.type_name not in SHAPE_COLLECTION_TYPES
    return has_key_name and is_non_collection


def annotate_shape_and_its_members_with_target_path(
    shape: Shape, target_str: str = ""
) -> Shape:

    if not shape or shape.name in BLACKLISTED_SHAPE_NAMES:
        return False

    if shape.type_name == "structure":
        new_target_str = target_str
        shape_key = getattr(shape, "key_name", "")
        if shape_key and target_str == "":  # target_str is empty, first time
            new_target_str = f"{shape_key}"
        elif shape_key and target_str != "":  # target_str is already available
            new_target_str = f"{target_str}[*].{shape_key}"
        setattr(shape, "target_path", new_target_str)
        
        for member_key, member in shape.members.items():
            setattr(member, "key_name", member_key)
            setattr(member, "parent_name", shape.name)
            annotate_shape_and_its_members_with_target_path(member, new_target_str)

    elif shape.type_name == "list":
        shape_key = getattr(shape, "key_name", "")
        new_target_str = target_str
        if shape_key and target_str == "":  # target_str is empty, first time
            new_target_str = f"{shape_key}"
        elif shape_key and target_str != "":  # target_str is already available
            new_target_str = f"{target_str}[*].{shape_key}"
        setattr(shape, "target_path", new_target_str)
        
        only_member = shape.member
        annotate_shape_and_its_members_with_target_path(only_member, new_target_str)
        # found_members_shapes.append(only_member)

    elif shape.type_name != "map":
        shape_name = getattr(shape, "key_name", shape.name)
        new_target_str = target_str
        if shape_name and target_str == "":  # target_str is empty, first time
            new_target_str = f"{shape_name}"
        elif shape_name and target_str != "":  # target_str is already available
            new_target_str = f"{target_str}[*].{shape_name}"
        setattr(shape, "target_path", new_target_str)

    return shape

    # members = get_members_shapes(shape)
    # for member in members:
    #     # create the target path for the member
    #     member_key_name = getattr(member, "key_name", False)
    #     new_target_str = target_str
    #     if member_key_name:
    #         if target_str == "":
    #             new_target_str = f"{member_key_name}"
    #         else:
    #             new_target_str = f"{target_str}[*].{member_key_name}"
    #     setattr(member, "target_path", new_target_str)
    #     # if member.type_name in ("structure", "list"):
    #     # if the member is a collection type, recurse into it
    #     # inner_list = _flatten_shape_to_its_members_and_target_paths(
    #     #     member, new_target_str
    #     # )

    # return shape


def _flatten_shape_to_its_members_and_target_paths(
    shape: Shape, target_str: str = ""
) -> List[ShapeAndTargetPath]:
    """Recursive function to get a shape's all members with targetpaths.
    Generates target_str JMESPath selector for each member as it's located in the hierarchy.
    Returns a flat list of (shape, target_path) namedtuples

    Args:
        shape (Shape): botocore shape, possibly output shape of an operation
        target_str (str, optional): Used for keeping track of the target path in recursion.

    Returns:
        List[ShapeAndTargetPath]: List of ShapeAndTargetPath NamedTuple
    """
    result = []
    members = get_members_shapes(shape)
    for member in members:
        member_key_name = getattr(member, "key_name", False)
        new_target_str = target_str
        if member_key_name:
            if target_str == "":
                new_target_str = f"{member_key_name}"
            else:
                new_target_str = f"{target_str}[*].{member_key_name}"
        if member.type_name in (
            "structure",
            "list",
        ):  # TODO:SHAPE_COLLECTION_TYPES-('map',):
            # if the member is a collection type, recurse into it
            inner_list = _flatten_shape_to_its_members_and_target_paths(
                member, new_target_str
            )
            result.extend(inner_list)
        else:
            result.append(ShapeAndTargetPath(member, new_target_str))
    return result


def flatten_shape_to_its_non_collection_shape_and_target_paths(
    shape: Shape,
) -> List[ShapeAndTargetPath]:
    """Return a flat list of shapes all member shapes w/ their JMESPath selector `target_path`

    Args:
        shape (Shape): botocore shape to list its members

    Returns:
        List[ShapeAndTargetPath]: (shape, target_path) custom namedtuple
    """
    # generate all possible members and their target paths
    all_flat_members_and_target_paths = _flatten_shape_to_its_members_and_target_paths(
        shape
    )
    # filter out the collection types beacuse they are not supported by JMESPath
    non_collection_shapes_and_target_paths = list(
        filter(is_shape_non_collection_type, all_flat_members_and_target_paths)
    )
    return non_collection_shapes_and_target_paths


def cleanhtml(raw_html: str) -> str:
    """Removes the HTML tags from given raw_html

    Args:
        raw_html (str): HTML string to clean the tags off of

    Returns:
        str: HTML with tags removed
    """
    cleantext = re.sub(HTML_CLEANER_REGEX, "", raw_html)
    return cleantext


def rich_str_shape(shape: Shape, remove_documentation=False) -> str:
    """Transforms a Shape to rich supported string.

    Args:
        shape (Shape): botocore.model.Shape object.

    Returns:
        str: Rich string for shape.
    """
    key_name = getattr(shape, "key_name", "")
    type_name = str(shape.type_name)

    shape_documentation = cleanhtml(shape.documentation)
    if remove_documentation:
        shape_documentation = ""

    target_path = getattr(shape, "target_path", "")
    if target_path:
        target_path = f"[].{target_path}[]"
        target_path = f"[green]{target_path}[/]"
    
    shape_str = (
        f"[blue bold]{key_name}[/] — ({type_name}) — {target_path}  {shape_documentation}"
    )
    if key_name == "":
        lead = ""
        if type_name == "list":
            lead = "["
        elif type_name == "structure":
            lead = "{"
        shape_str = f"[red]{escape(lead)}[/] — ({type_name}) — {target_path}  [gray]{shape_documentation}[/]"

    return shape_str


def generate_rich_tree_from_shape(shape: Shape, remove_documentation=False) -> Tree:
    """Genereate a rich Tree containing `shape` and it's members."""
    tree = Tree(rich_str_shape(shape), guide_style="red")

    shape = annotate_shape_and_its_members_with_target_path(shape)
    
    def _recursive_stringify_shape(shape, node: Tree, remove_documentation=False):

        members = get_members_shapes(shape)
        for member in members:
            member_str = rich_str_shape(member, remove_documentation=remove_documentation)
            if member.type_name in SHAPE_COLLECTION_TYPES:
                new_node = node.add(member_str)
                _recursive_stringify_shape(member, new_node, remove_documentation=remove_documentation)
            else:
                node.add(member_str)

    _recursive_stringify_shape(shape, tree, remove_documentation=remove_documentation)
    return tree


# @lru_cache(maxsize=500) # print(get_shape_name.cache_info())
def get_shape_name(shape: Shape) -> str:
    """Returns the shapes name, using custom set 'key_name' attr

    Args:
        shape (Shape): botocore Shape obj

    Returns:
        str: Name of the shape.
    """
    shape_name = shape.name
    shape_key_name = getattr(shape, "key_name", False)
    if shape_name.lower() in UNWANTED_SHAPE_NAMES_LOWERED:
        # check for name forgotten in shape.serialization if the name is a type name.
        if shape_key_name:
            return shape_key_name
        elif shape.serialization and shape.serialization.get("name", False):
            given_serialization_name = shape.serialization.get("name")
            return given_serialization_name
    if shape_key_name:
        return shape_key_name
    return shape_name


def get_required_parameter_shapes_from_operation_model(
    operation_model: OperationModel,
) -> List[Shape]:
    """Finds required parameter shapes of the operation models input_shape.

    Args:
        operation_model (OperationModel): botocore OperationModel obj of the Operation

    Returns:
        List[Shape]: Required parameter shapes.
    """
    input_shape = get_input_shape(operation_model)
    if not input_shape:
        return []  # there's no input shape
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
