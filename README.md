# balcony

AWS API for us humans.

Balcony helps to lift the undifferentiated heavy lifting that is reading from AWS SDK & API.

Balcony fills out the **required parameters** for any operation, automatically. 


## Installation

```bash
pip3 install balcony

python3 -m pip install balcony
```


## Basic Usage
#### List all available AWS Services

```bash
balcony aws
```
#### List all Resource Nodes of a Service
```bash
balcony aws iam

balcony aws ec2
```
#### See the documentation of a Resource Node and its Operations
```bash
balcony aws iam Policy -l
# or
balcony aws iam Policy --list
```


#### Read a Resource Node


```bash
balcony aws iam Policy

# if you are curious to see what's going on 
# under the hood, enable the debug messages 
balcony aws iam Policy -d
# or
balcony aws iam Policy --debug
```
#### Read a Resource Nodes specific operation

```bash
balcony aws iam Policy get

balcony aws iam Policy list
```

#### Filter generated parameters with UNIX style pattern matching
```bash
balcony aws iam Policy get  -p "*service-role/*"

# supports multiple patterns 
balcony aws iam Policy -p "*service-role/*" -p "*prod-*"

```

#### Use queries for the json data -- like `jq`
```bash
balcony aws iam Policy \
    --jmespath-selector "GetPolicy[*].Policy"
# or
balcony aws iam Policy \
    -js "GetPolicy[*].Policy"
```

#### Use `--format` option for customized output

```bash
# create stop-instances script for running instances
balcony aws ec2 Instances \
    -js "DescribeInstances[*].Reservations[*].Instances[?State.Name=='running'][][]" \
    --format "aws ec2 stop-instances --instance-ids {InstanceId} # {Tags}"

# create delete-policy script
balcony aws iam Policy \
    --jmespath-selector "GetPolicy[*].Policy" \
    --format "aws iam delete-policy --policy-arn {Arn}"
```