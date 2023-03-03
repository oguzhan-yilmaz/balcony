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

For each available service name, its `client` is created.


Every `client` has a `_PY_TO_OP_NAME` mapping that looks like this:

| key | value | 
|:-- |:-- | 
| attach_role_policy | AttachRolePolicy |
| detach_role_policy | DetachRolePolicy |
| create_role | CreateRole |
| delete_role | DeleteRole |
| get_role | GetRole |

`_PY_TO_OP_NAME` represents a mapping from the python function names to actual HTTP API operation names. 

!!! note ""

    AWS API Operation names follows a nice `Verb`+`Resource(s)` convention. 

    Read-only operations only have `Get`, `List`, `Describe` verbs.




### balcony only uses the **read-only** operations 

Balcony only uses the Operation names starting with `Get`, `List`, `Describe` verbs.

Let's take the a look at `IAM` client, and how `balcony` groups them together.

**Quick look at some of the IAM operations**

| get operations | list operations |
|-- |--|
| **Get**Group | **List**Groups |
| **Get**GroupPolicy | **List**GroupPolicies |
| **Get**Policy | **List**Policies |
| **Get**Role | **List**Roles |
| **Get**RolePolicy | **List**RolePolicies |
| **Get**User | **List**Users |


**Operations can be grouped under their resource names**

Naming convention allows parsing CamelCase operation names to `Verb`+`ResourceNodeName`.

| Resource Node | Operations |
|-- |--|
| Group | **Get**Group, **List**Groups |
| GroupPolicy | **Get**GroupPolicy, **List**GroupPolicies |
| Policy | **Get**Policy, **List**Policies |
| Role | **Get**Role, **List**Roles |
| RolePolicy | **Get**RolePolicy, **List**RolePolicies |
| User | **Get**User, **List**Users |


Some operations have the same `ResourceNodeName` but a different `Verb`. These operations are grouped under their respective `ResourceNode`. 


```txt title="Composition of ServiceNode, ResourceNode and Operations"
ServiceNode: (iam)
│
├── ResourceNode: (Role)
│   └── Operations
│       ├── GetRole
│       └── ListRoles
│
└── ResourceNode: (Policy)
    └── Operations
        ├── GetPolicy
        └── ListPolicies
```
