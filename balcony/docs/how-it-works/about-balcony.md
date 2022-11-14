# About balcony

**AWS Services**

`boto3 Session`

```python
import boto3
services = boto3.session.Session().get_available_services()
```



Balcony only uses the ReadOnly Operations. 



**Quick look at the IAM operations**

| get operations | list operations |
|-- |--|
| **Get**Group | **List**Groups |
| **Get**GroupPolicy | **List**GroupPolicies |
| **Get**Policy | **List**Policies |
| **Get**Role | **List**Roles |
| **Get**RolePolicy | **List**RolePolicies |
| **Get**User | **List**Users |

**Operations can be grouped under their resource names**

| Resource Node | Operations |
|-- |--|
| Group | **Get**Group, **List**Groups |
| GroupPolicy | **Get**GroupPolicy, **List**GroupPolicies |
| Policy | **Get**Policy, **List**Policies |
| Role | **Get**Role, **List**Roles |
| RolePolicy | **Get**RolePolicy, **List**RolePolicies |
| User | **Get**User, **List**Users |


