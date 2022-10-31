# How Balcony Works


## Example 
```python
import boto3
iam_client = boto3.client('iam')
policies_response = iam_client.list_policies()
policies = policies_response.get('Policies')
for policy in policies:
    p_version_response = iam_client.get_policy_version(
        PolicyArn=policy.get('Arn'),
        VersionId=policy.get('DefaultVersionId')
    )
    p_version = p_version_response.get('PolicyVersion')
    print(p_version)


```