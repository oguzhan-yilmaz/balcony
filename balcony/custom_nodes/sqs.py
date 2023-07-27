from nodes import ResourceNode
from config import get_logger
from relations import Relation
import jmespath

logger = get_logger(__name__)

class GroupPolicy(ResourceNode, service_name="sqs", name="QueueUrl"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_operations_relations(self, operation_name: str):
        if operation_name == "GetQueueUrl":
            return [
                Relation(
                    **{
                        "service_name": "sqs",
                        "resource_node_name": "Queues",
                        "operation_name": "ListQueues",
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
        if operation_name == "GetQueueUrl":
            generated_api_parameters = []

            # select non-empty PolicyNames lists
            queue_urls = jmespath.search(
                "ListQueues[].QueueUrls[]", related_operations_data
            )
            for queue_url in queue_urls:
                queue_name = queue_url.split("/")[-1]
                generated_api_parameters.append({"QueueName": queue_name})
            return generated_api_parameters, None

        # if this is NOT our selected operation, let the normal flow run
        return super().generate_api_parameters_from_operation_data(
            operation_name, relations_of_operation, related_operations_data
        )
