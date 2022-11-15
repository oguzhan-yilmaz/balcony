# About **boto3** and AWS SDK & API


**Size of AWS SDK & API**

| Type | Count | 
|:-- |:-- | 
| Services | 318+ | 
| ReadOnly Operations | 4577+ | 
| All Operations | 12129+ | 

`boto3` is only a wrapper for the existing AWS HTTP API.

AWS team didn't code each operation of `boto3` individually for Python, that'd be not productive.

Instead, they used [underlying service definition json files](https://github.com/boto/botocore/blob/develop/botocore/data/iam/2010-05-08/service-2.json) which is used to generate all of AWS Services. 

```python 
import boto3
iam_client = boto3.client('iam')
```

You can see that we refer to services by variable name, instead of accessing as a composite object, like `boto3.iam()` — _hinting at its generated nature_.



**Service definition json files**

Encapsulates everything needed for making every API request exist in a service:

- endpoint — URI
- input format — Parameters
- output format — Response
- possible errors — Exceptions

### Outline of boto service definitions 
 _botocore/botocore/data/**iam**/2010-05-08/service-2.json_


**json outline**
```json
{
  "version":"2.0",
  "metadata": {...},
  "operations":{...},
  "shapes":{...},
  "documentation": "..."
}
```
**metadata**

Defines the metadata of an AWS Service.

```json
"metadata":{
    "apiVersion":"2010-05-08",
    "endpointPrefix":"iam",
    "globalEndpoint":"iam.amazonaws.com",
    "protocol":"query",
    "serviceAbbreviation":"IAM",
    "serviceFullName":"AWS Identity and Access Management",
    "serviceId":"IAM",
    "signatureVersion":"v4",
    "uid":"iam-2010-05-08",
    "xmlNamespace":"https://iam.amazonaws.com/doc/2010-05-08/"
}
```


**shapes**

`Shape` is a nested data abstraction that is able to represent any data structure, created by `boto` team.

Every data type used in a service is available on `.shapes` definition. 

```json
"shapes":{
    "GetPolicyRequest":{
        "type":"structure",
        "required":["PolicyArn"],
        "members":{
            "PolicyArn":{
              "shape":"arnType",
              "documentation":"The Amazon Resource Name(ARN)
                               of the managed policy"
            }
        }
    }
}
```

**operations**

Types of requests you can make to AWS API are internally called `Operation`.


Operations define `input_shape` and `output_shape` for its input and output data structure. It also defines the required parameters for an operation. And also the possible exceptions you might get calling this operation.

```json
"operations":{
    "GetPolicy":{
      "name":"GetPolicy",
      "http":{
        "method":"POST",
        "requestUri":"/"
      },
      "input":{"shape":"GetPolicyRequest"},
      "output":{
        "shape":"GetPolicyResponse",
        "resultWrapper":"GetPolicyResult"
      },
      "errors":[
        {"shape":"NoSuchEntityException"},
        {"shape":"InvalidInputException"},
        {"shape":"ServiceFailureException"}
      ],
      "documentation":"<p>Retrieves information about the 
      specified managed policy, including the policy's default 
      version and the..."
    }
}
```



#### boto3 service clients & their operations


Every boto3 client has a `_PY_TO_OP_NAME` mapping that looks like this:

| boto3 client function | Operation Name | 
| -- | -- | 
| attach_role_policy | AttachRolePolicy |
| create_role | CreateRole |
| delete_role | DeleteRole |
| detach_role_policy | DetachRolePolicy |
| get_role | GetRole |

This represents a mapping from the python function names to actual operation names. 

You might be already familiar with `Operations` because they are the exact same thing as the **Action** segment on IAM Policies.

**Example IAM Policy**
```json
{
  "Statement": [
    {
        "Effect": "Allow",
        "Resource": "*",
        "Action": [
            "cloudwatch:Describe*",
            "ec2:DescribeSubnets",
            "ec2:DescribeVpcs",
            "iam:ListRoles",
            "iam:GetRole",
            "logs:Create*"
        ]
    }
  ]
}
```

## Something is _generated_ about **boto3**...

In Python, everything is an object. Even the `modules` are objects.

```python
import boto3
# print the symbols of boto3
print(dir(boto3))
```

When a module is imported, it can be queried for its composite objects on runtime. 

AWS SDK exposes the AWS API on service basis, accessible through service `clients`. 

```python
iam_client = boto3.client('iam')
```
