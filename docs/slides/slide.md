---
marp: true
---

# [balcony](https://github.com/oguzhan-yilmaz/balcony) 

AWS API for us humans. _beep boop._ 




---
# Agenda
0. What balcony helps with
1. About the AWS SDK & API
2. How balcony works
3. 


---
# What do balcony do?

- balcony trivializes reading anything from AWS API
- You only need to provide the `service name` and `resource name` and data is yours
- For example:
  ```bash
  balcony aws iam Policy

  balcony aws ec2 Vpcs
  ```
---
# Undifferentiated heavy lifting that is reading from SDK

- Detail views almost always require an identifier (`GetPolicy` - `PolicyArn`)
- Subresources requires their parent resources id (`BucketPolicy` - `BucketName`)

<br/>

balcony fills out the **required parameters** for any operation, automatically.

<br/>

Let's take the above example of `GetUserPolicy`:

- balcony would first read every `User`
- and then it'd feed the each `UserName` to the `GetUserPolicy` operation.




---
# How'd it look on code
```python
import boto3
iam_client = boto3.client('iam')
# First get the list of all policies
all_policies = iam_client.list_policies()

# and then get detail per policy 
for policy in all_policies.get('Policies'):
  single_policy = iam_client.get_policy(
      PolicyArn = policy['Arn']
  )
```

---
# Let's talk about AWS SDK & API

- AWS SDK for Python3 is [boto3](https://github.com/boto/boto3), and it uses the [botocore](https://github.com/boto/botocore) under the hood
- boto3 is the Python3 **wrapper** for the AWS  HTTP API

## Sheer size of AWS SDK



| Type | Count | 
|:-- | -- | 
| Service | 318 | 
| Read Only Operations | 4577 | 
| All Operations | 12129 | 


---
# Rhetoric: How'd you write a SDK for an existing API?
## Possibly you'd consider the scale of it, right?
- wouldn't make sense to code each operation on its own
- maybe ReInvent is closing in, and you'd get more services & operations to code
- oh, and there're many languages to code the SDK for



---
# Answer is **automation**, as always

Good people at AWS did a great job at this.

In fact, whole boto3 functionality is generated from `json`


```python
import boto3

iam_client = boto3.client('iam')
```

You can see that we refer to services by name, instead of accessing composite objects, like `boto3.iam` — _hinting at its generated nature_.

---
# Service definition json files

Encapsulates everything needed for making an API Request:
- endpoint — URI
- input format — Parameters
- output format — Response
- possible errors — Exceptions

---
## Outline of Boto Service definitions 
 _botocore/botocore/data/**iam**/2010-05-08/service-2.json_

```json
{
  "version":"2.0",
  "metadata": {...},
  "operations":{...},
  "shapes":{...},
  "documentation": "..."
}
```
---
## Boto Service definitions: **metadata**
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

---

## Boto AWS Service definitions: **shapes**
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

---
## Boto AWS Service definitions: **operations**
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



---
# boto3 clients & operations


Every boto3 client has a `_PY_TO_OP_NAME` mapping that looks like this:
> Types of requests you can make to AWS API are internally called **`Operation`**

| boto3 client function | Operation Name | 
| -- | -- | 
| attach_role_policy | AttachRolePolicy |
| create_role | CreateRole |
| delete_role | DeleteRole |
| detach_role_policy | DetachRolePolicy |
| get_role | GetRole |
---

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
            "logs:Create*",
        ]
    }
  ]
}
```

---
# How balcony works
- only uses the Read Only Operations
- 

---
## quick look at the IAM operations
| get operations | list operations |
|-- |--|
| **Get**Group | **List**Groups |
| **Get**GroupPolicy | **List**GroupPolicies |
| **Get**Policy | **List**Policies |
| **Get**Role | **List**Roles |
| **Get**RolePolicy | **List**RolePolicies |
| **Get**User | **List**Users |

---
## operations can be grouped under their resource names
| Resource Node | Operations |
|-- |--|
| Group | **Get**Group, **List**Groups |
| GroupPolicy | **Get**GroupPolicy, **List**GroupPolicies |
| Policy | **Get**Policy, **List**Policies |
| Role | **Get**Role, **List**Roles |
| RolePolicy | **Get**RolePolicy, **List**RolePolicies |
| User | **Get**User, **List**Users |

---












---
## How to read the IAM policies


