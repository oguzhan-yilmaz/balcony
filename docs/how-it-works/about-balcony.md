# balcony and boto3

**Listing AWS Services**

All available AWS Services for the current region can be queried using boto3.

```python title="Listing available service names"
session = boto3.session.Session()
session.get_available_services()
# ['accessanalyzer', 'account', 'acm', 'acm-pca', 'alexaforbusiness', ...]
```

## Python lets you inspect anything on runtime

In Python, everything is an object. Even the `modules` are objects.

When a module is `import`ed, it can be queried for its composite objects on runtime. 

```python title="Listing boto3 scope"
print(dir(boto3))
# [..., '__version__, 'client', 'docs','resources', 'session', 'utils']
```

AWS SDK exposes the AWS API on service basis, accessible through service `clients`. 

```python
iam_client = boto3.client('iam')
```


## balcony parses boto3 clients

For each available AWS service, its `boto3.client` is created and parsed for it's functions.


Every `client` has a `_PY_TO_OP_NAME` mapping that looks like this:

| key | value | 
|:-- |:-- | 
| attach_role_policy | AttachRolePolicy |
| detach_role_policy | DetachRolePolicy |
| create_role | CreateRole |
| delete_role | DeleteRole |
| get_role | GetRole |

`_PY_TO_OP_NAME` represents a mapping from the pythonic function names ==to actual AWS HTTP API operation names.== 

!!! note ""

    AWS API Operation names follows a nice `Verb`+`Resource(s)` convention. 

    Read-only operations have `Get`, `List`, `Describe` verbs.



## balcony only uses the **read-only** operations 

Balcony only uses the Operation names starting with `Get`, `List`, `Describe` verbs.

This means that it won't take any action on your AWS account other than reads.



### Quick look at some of the IAM operations

Let's take the a look at `IAM` client, and how `balcony` groups them together.

Here's some IAM operations:

| get operations | list operations |
|-- |--|
| **Get**Group | **List**Groups |
| **Get**GroupPolicy | **List**GroupPolicies |
| **Get**Policy | **List**Policies |
| **Get**Role | **List**Roles |
| **Get**RolePolicy | **List**RolePolicies |
| **Get**User | **List**Users |


### Operations can be grouped under their resource names

Naming convention allows parsing CamelCase operation names to `Verb`+`ResourceNodeName(s)` format. Plurality is also taken into account.

Some operations have the same `ResourceNodeName` but a different `Verb`. 


| Resource Node | Operations |
|-- |--|
| Group | **Get**Group, **List**Groups |
| GroupPolicy | **Get**GroupPolicy, **List**GroupPolicies |
| Policy | **Get**Policy, **List**Policies |
| Role | **Get**Role, **List**Roles |
| RolePolicy | **Get**RolePolicy, **List**RolePolicies |
| User | **Get**User, **List**Users |

These operations are grouped under their respective `ResourceNode`.  Here's the tree view of an example resource node:

```txt title="Composition of ServiceNode, ResourceNode and Operations"
ServiceNode: (iam)
│
├── ResourceNode: (Role)
│   └── operation_names: list
│       ├── GetRole
│       └── ListRoles
│
└── ResourceNode: (Policy)
    └── operation_names: list
        ├── GetPolicy
        └── ListPolicies
```
