from aws import BalconyAWS
from terraform_import.main import main as terraform_import_main

balcony_aws = BalconyAWS()
tf_import_blocks = terraform_import_main(balcony_aws, "ec2", "Instances")
print('\n\n'.join(tf_import_blocks))

tf_import_blocks = terraform_import_main(balcony_aws, "s3", "Buckets")
print('\n\n'.join(tf_import_blocks))
tf_import_blocks


# from utils import is_word_in_a_list_of_words
# from typing import Dict, List, Union
# from nodes import PAGINATION_TOKEN_KEYS

# def get_pagination_token_output_to_parameter_name_mapping(
#     self, operation_name: str
# ) -> Union[Dict[str, str], bool]:
#     """Some Operations paginate their output using Pagination Token Parameters defined in `PAGINATION_TOKEN_KEYS`.

#     Args:
#         resource_node (ResourceNode): _description_
#         operation_name (str): Name of the operation in the resource_node.

#     Returns:
#         Union[Dict[str, str], bool]: False or A dictionary with `parameter_name` and `output_key` keys. e.g. `{"parameter_name":"nextToken", "output_key": "NextToken"}`.
#     """
#     resource_node = self

#     # find all parameter names that are in `PAGINATION_TOKEN_KEYS`, case insensitive
#     parameter_names = [
#         pn
#         for pn in resource_node.get_all_parameter_names_from_operation_name(
#             operation_name
#         )
#         if is_word_in_a_list_of_words(pn, PAGINATION_TOKEN_KEYS)
#     ]

#     #  find all output keys that are in `PAGINATION_TOKEN_KEYS`, case insensitive
#     output_keys = [
#         ok
#         for ok in resource_node.get_all_output_keys_from_operation_name(
#             operation_name
#         )
#         if is_word_in_a_list_of_words(ok, PAGINATION_TOKEN_KEYS)
#     ]

#     if output_keys and parameter_names

#         return {
#             "parameter_name": parameter_names[0],
#             "output_key": output_keys[0],
#         }
#     return False


# def main():
#     baws = BalconyAWS()
#     aws_services = baws.get_available_service_names()
#     for aws_service_name in aws_services[aws_services.index("lexv2-runtime") :]:
#         print(aws_service_name)
#         service_node = baws.get_service_node(aws_service_name)
#         for resource_node in service_node.get_resource_nodes():
#             for operation_name in resource_node.get_operation_names():
#                 a = get_pagination_token_output_to_parameter_name_mapping(
#                     resource_node, operation_name
#                 )
#                 print(a)

#                 # "nexttoken, continuationtoken, marker"
#                 # rpp = [_ for _ in rp if "token" in _.lower() or "marker" in _.lower()]
#                 # opp = [_ for _ in op if "token" in _.lower() or "marker" in _.lower()]
#                 # if rpp or opp:
#                 #     print(
#                 #         f"  {operation_name} :: {','.join(rpp)} --::-- {','.join(opp)}"
#                 #     )


# def __():
#     pass


# main()
