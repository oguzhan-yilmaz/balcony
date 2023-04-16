# About **boto3** and AWS API

Boto3 is the Amazon Web Services Software Development Kit (AWS SDK) for Python, which allows Python developers to write software that makes use of AWS services.

`boto3` is simply a Python wrapper for the existing AWS HTTP API, providing pythonic functions to match the corresponding AWS API Operation.

AWS HTTP API is constantly being updated, and the SDKs must match them. We can infer that AWS team has to maintain multitude of SDKs for the popular programming languages, and have them match the HTTP API.

**Absolute unit size of the AWS SDK & API**

| Entity Type          | Count  |
| :------------------- | :----- |
| Services             | 318+   |
| Read-only Operations | 4577+  |
| All Operations       | 12129+ |

Instead of creating a python function that'd make a call to AWS HTTP API, `botocore` team opted to abstract the whole API definition to underlying service `.json` files.

```python
import boto3
iam_client = boto3.client('iam')
```

When you create a `boto3.client` object like this, the underlying JSON files are used to dynamically create clients during runtime. These files are versioned to match the API.

You also can see that we get clients by providing their string names, instead of accessing them as composite objects, like `boto3.iam` — _hinting at its generated nature_.

#### Service definition json files

These files are defined in the [botocore/data/\*\*/](https://github.com/boto/botocore/tree/develop/botocore/data) for each AWS Service.

For example, you can inspect the [AWS IAM Service botocore service definition json](https://github.com/boto/botocore/blob/develop/botocore/data/iam/2010-05-08/service-2.json) file.

These files encapsulate everything needed for making every API request exist in a service:

- **endpoint** — URI
- **input format** — Parameters
- **output format** — Response
- **possible errors** — Exceptions

### Outline of boto service definitions



**json outline**

```json title="botocore/botocore/data/iam/2010-05-08/service-2.json" 
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

`Shape`s are used to define function input & output structures.

Every data type used in a service is available on it's `.shapes` definition.

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

==Types of requests(API calls) you can make to AWS API are internally called `Operation`.==

Operations define `input_shape` and `output_shape` for its input & output data structure. It also defines the required parameters for an operation. And also the possible exceptions you might get calling this operation.

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

### boto3 service clients & their operations

Every boto3 client has a `_PY_TO_OP_NAME` mapping that looks like this:

| boto3 client function | Operation Name   |
| --------------------- | ---------------- |
| attach_role_policy    | AttachRolePolicy |
| create_role           | CreateRole       |
| delete_role           | DeleteRole       |
| detach_role_policy    | DetachRolePolicy |
| get_role              | GetRole          |

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
