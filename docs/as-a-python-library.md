# Balcony as a Python Library

### Using custom boto3 Session

Balcony will use the AWS credentials in your environment by default.

You can configure the [boto3 Session](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/session.html) in your code and pass it to Balcony. 

```python
from balcony import BalconyAWS

boto3_session = boto3.session.Session(
    aws_access_key_id='...',
    aws_secret_access_key='...',
    aws_session_token = '...',
    region_name='...',
    profile_name = '...'
)

baws = BalconyAWS(boto3_session)
```

### Listing available AWS services 

```python
from balcony import BalconyAWS
baws = BalconyAWS()

service_names = baws.get_available_service_names()
print(service_names)

```

### Reading a Resource Node 

This operation read all operations for given `resource_node_name`.

For example, if `iam.Policy` has `GetPolicy` and `ListPolicies` operations, so both of them will be read.

```python
from balcony import BalconyAWS
baws = BalconyAWS()

all_policies = baws.read_resource_node('iam', 'Policy')
print(all_policies)
```

### Reading a specific Operation

You can read a single operation

```python
from balcony import BalconyAWS
baws = BalconyAWS()

policies = baws.read_operation(
    service_name: 'iam',
    resource_node_name: 'Policy',
    operation_name: 'ListPolicies'
)
print(policies)
```


