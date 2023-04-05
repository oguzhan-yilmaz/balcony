from nodes import ResourceNode
from config import get_logger
from relations import Relation
import jmespath

logger = get_logger(__name__)


class RolePolicy(ResourceNode, service_name="iam", name="RolePolicy"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_operations_relations(self, operation_name: str):
        """
        Relations defined in this function overrides the auto generated relations.
        Operations given in the relations are promised to be called before the current operation.
        And the related operations data will be passed to the generate_api_parameters_from_operation_data function.

        `GetRolePolicy` operations parameters can be generated from the `ListRolePolicies` operations output.
        """
        if operation_name == "GetRolePolicy":
            return [
                Relation(
                    **{
                        "service_name": "iam",
                        "resource_node_name": "RolePolicy",
                        "operation_name": "ListRolePolicies",
                        "required_shape_name": "PolicyName",
                        "target_shape_name": "PolicyNames",
                        "target_shape_type": "list",
                        "target_path": "--ommitted--",
                    }
                )
            ], None

        return super().get_operations_relations(operation_name)

    def generate_api_parameters_from_operation_data(
        self, operation_name, relations_of_operation, related_operations_data
    ):
        """
        GetRolePolicy requires RoleName and PolicyName as parameters which can be found in the ListRolePolicies output.
        The reason to override this method is to generate the valid required parameters which was not possible with only the jmespath query.

        ListRolePolicies output data looks like this:
        ```
        [
            {
                "PolicyNames": [
                    "_policy_name_1",
                    "_policy_name_2"
                ],
                "IsTruncated": false,
                "__args__": {
                    "RoleName": "_role_name"
                }
            },
        ]
        ```

        and GetRolePolicy operation requires {"RoleName":..., "PolicyName":...} as parameters.
        This function generates the required parameters from the ListRolePolicies output if the operation is GetRolePolicy.
        """
        if operation_name == "GetRolePolicy":
            generated_api_parameters = []

            # select non-empty PolicyNames lists
            non_empty_policy_names = jmespath.search(
                "ListRolePolicies[?length(PolicyNames) > `0`]", related_operations_data
            )
            for data in non_empty_policy_names:
                role_name = data.get("__args__").get("RoleName")
                policy_names = data.get("PolicyNames")
                for policy_name in policy_names:
                    generated_api_parameters.append(
                        {"RoleName": role_name, "PolicyName": policy_name}
                    )
            return generated_api_parameters, None

        # if this is NOT our selected operation, let the normal flow run
        return super().generate_api_parameters_from_operation_data(
            operation_name, relations_of_operation, related_operations_data
        )


class UserPolicy(ResourceNode, service_name="iam", name="UserPolicy"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_operations_relations(self, operation_name: str):

        if operation_name == "GetUserPolicy":
            return [
                Relation(
                    **{
                        "service_name": "iam",
                        "resource_node_name": "UserPolicy",
                        "operation_name": "ListUserPolicies",
                        "required_shape_name": "--ommitted--",
                        "target_shape_name": "--ommitted--",
                        "target_shape_type": "--ommitted--",
                        "target_path": "--ommitted--",
                    }
                )
            ], None

        return super().get_operations_relations(operation_name)

    def generate_api_parameters_from_operation_data(
        self, operation_name, relations_of_operation, related_operations_data
    ):
        if operation_name == "GetUserPolicy":
            generated_api_parameters = []

            # select non-empty PolicyNames lists
            non_empty_policy_names = jmespath.search(
                "ListUserPolicies[?length(PolicyNames) > `0`]", related_operations_data
            )
            for data in non_empty_policy_names:
                user_name = data.get("__args__").get("UserName")
                policy_names = data.get("PolicyNames")
                for policy_name in policy_names:
                    generated_api_parameters.append(
                        {"UserName": user_name, "PolicyName": policy_name}
                    )
            return generated_api_parameters, None

        # if this is NOT our selected operation, let the normal flow run
        return super().generate_api_parameters_from_operation_data(
            operation_name, relations_of_operation, related_operations_data
        )


class GroupPolicy(ResourceNode, service_name="iam", name="GroupPolicy"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_operations_relations(self, operation_name: str):

        if operation_name == "GetGroupPolicy":
            return [
                Relation(
                    **{
                        "service_name": "iam",
                        "resource_node_name": "GroupPolicy",
                        "operation_name": "ListGroupPolicies",
                        "required_shape_name": "--ommitted--",
                        "target_shape_name": "--ommitted--",
                        "target_shape_type": "--ommitted--",
                        "target_path": "--ommitted--",
                    }
                )
            ], None

        return super().get_operations_relations(operation_name)

    def generate_api_parameters_from_operation_data(
        self, operation_name, relations_of_operation, related_operations_data
    ):
        if operation_name == "GetGroupPolicy":
            generated_api_parameters = []

            # select non-empty PolicyNames lists
            non_empty_policy_names = jmespath.search(
                "ListGroupPolicies[?length(PolicyNames) > `0`]", related_operations_data
            )
            for data in non_empty_policy_names:
                group_name = data.get("__args__").get("GroupName")
                policy_names = data.get("PolicyNames")
                for policy_name in policy_names:
                    generated_api_parameters.append(
                        {"GroupName": group_name, "PolicyName": policy_name}
                    )
            return generated_api_parameters, None

        # if this is NOT our selected operation, let the normal flow run
        return super().generate_api_parameters_from_operation_data(
            operation_name, relations_of_operation, related_operations_data
        )
