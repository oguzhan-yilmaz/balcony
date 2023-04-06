# About Relations

`Relation` is a basic dataclass that holds the information about the relation between the operations of the AWS services.

It's basically a description of where to find a required parameter's value in another operation's output.

Balcony traverses each operation, and finds the required parameters. Then it tries to find the Relations among required parameters and other operations outputs.

It can't always find the right relations, so some customization might be needed for some operations.


```python title="Relation class"
@dataclass
class Relation:
    service_name: str        # AWS service name
    resource_node_name: str  # ResourceNode name
    operation_name: str      # given ResourceNode's specific operation name
    required_shape_name: str # Required parameter name for other operations
    target_shape_name: str   # Dict Key name from operation's output
    target_shape_type: str   # Data type of the `target_shape_name`
    target_path: str         # JMESPath selector for extracting the parameter values
```

## Example Relation & How to read it
```json title="Example Relation"
{
  "service_name": "iam",
  "resource_node_name": "Policy",
  "operation_name": "ListPolicies",
  "required_shape_name": "PolicyArn",
  "target_shape_name": "Arn",
  "target_shape_type": "string",
  "target_path": "Policies[*].Arn"
}
```

We could read this example relation like this:

- `iam` service has a `Policy` resource node, which has a `ListPolicies` operation.
- `"Arn"` is the key name of the output dictionary of the `ListPolicies` operation which has a `"string"` type.
- `required_shape_name`: `"PolicyArn"` is the name of the required parameter that could be populated using the `target` data.


So if any operation had a `PolicyArn` as a required parameter, we could use the `ListPolicies` operation to get the `Arn` value from the output dictionary.

`target_path` is a JMESPath query to extract the `Arn` value from the output dictionary.

