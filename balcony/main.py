try:
    from .custom_nodes import *
    from .nodes import *
    from .logs import get_logger
    from .factories import Boto3SessionSingleton
    from .utils import get_all_available_services, _create_boto_session
    from .registries import AppRegistry, app_registry
except ImportError:
    from custom_nodes import *
    from nodes import *
    from logs import get_logger, get_rich_console
    from factories import Boto3SessionSingleton
    from utils import get_all_available_services, _create_boto_session
    from registries import AppRegistry, app_registry

    from custom_nodes import *


import boto3
import sys

logger = get_logger(__name__)
console = get_rich_console()

# print(app_registry.app_configs)
# print(app_registry.app_configs)
# x = AppConfig.create('balcony_app.myservice')
# print(x)
# x




"""
1. check for already existing operation data
2. get relations of the operation
3. find the dependent operations to call
4. read the target dependent operation
5. generate JMESpath selectors with the relations
6. search with JMESpath to get raw_parameters
7. generate real api parameters from raw_parameters
8. read the current operation
"""
if __name__ == '__main__':
    # session = boto3.session.Session()
    session = Boto3SessionSingleton().get_session()
    all_service_names = get_all_available_services(session)
    success_count, failure_count, non_req_count = 0,0, 0
    
    service_node = ServiceNode('ec2', session)
    # service_node = ServiceNode('accessanalyzer', session)
    # service_reader = ServiceReader(service_node)

    # aa = service_reader.read_operation('PasswordData', 'GetPasswordData')
    # aa = service_reader.read_operation('AccessAnalyzer', 'GetAccessAnalyzer')
    # aa = service_reader.read_operation('NetworkInsightsAccessScopeAnalyses', 'DescribeNetworkInsightsAccessScopeAnalyses')
    # aa = service_reader.read_operation('ChangeSet', 'ListChangeSets')
    
    # aa

    # aa = service_reader.read_operation('Instances', 'DescribeInstances')
    # aa = service_reader.read_operation('SecurityGroups', 'DescribeSecurityGroups')
    # if aa:
    #     aa
    # for service_name in all_service_names:
        # continue
    # for service_name in []:
    for service_name in ['s3']:
        service_node = ServiceNode(service_name, session)
        service_node
        
   

        console.print('-'*50)
        console.print('#'*10, colored(service_name, 'yellow'), '#'*10)
        # resource_nodes = service_node.get_resource_nodes()
        service_reader = service_node.get_service_reader()


        read_operation_names = service_node.get_read_operation_names()
        for r_ops_name in read_operation_names:
            verb, *resource_name_tokens = camel_case_split(r_ops_name)
            resource_name = ''.join(resource_name_tokens)
            a = service_reader.read_operation(resource_name, r_ops_name)
    # #         # x = relation_map.find_best_relations_for_operations_parameters(r_ops_name)
            console.print(a)
            console.print('-'*40)
    #         if x:
    #             if len(x) == 1:
    #                 non_req_count+= 1
    #             success_count += 1 
    #         else:
    #             failure_count += 1
            
            
    #         # get_required_parameter_names_from_operation_name()
    #         print_flag = False
    #         if type(x)==dict:
    #             for _item in x.values():
    #                 if type(_item) in [dict, list]:
    #                     print_flag = True
    #                     break
    #         if print_flag:
    #             print(json.dumps(x, indent=2, default=str))
    #         if x:
    #             print( json.dumps(x, indent=2, default=str))
    #         else:
    #             print(colored('\t'+r_ops_name+'   FALSE', 'red'))
    #     print('SUCCESS', success_count)
    #     print('FAILURE', failure_count)
    #     print('NON_REQUIRED_PARAMS', non_req_count)
    #     print('TOTAL', success_count+failure_count)