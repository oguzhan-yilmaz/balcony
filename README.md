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

!!! tip "balcony will stick to your shell for the AWS credentials" 

    ```bash  title="See the active profile with awscli"
    aws sts get-caller-identity
    ```

    ```bash  title="Set your AWS profile and region"
    export AWS_PROFILE=default
    export AWS_REGION=us-east-1
    ```

    ```bash  title="Set your AWS credentials"
    export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
    export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
    export AWS_DEFAULT_REGION=us-west-2
    ```



```bash title="List all available AWS Services"
balcony aws
```

```bash title="List all Resource Nodes of a Service"
balcony aws iam

balcony aws ec2
```
!!! info "Remember to get **--help**" 

    ```bash  title=""
    balcony --help
    balcony aws --help
    ```

```bash title="See the documentation of a Resource Node and its Operations"
balcony aws iam Policy -l
# or
balcony aws iam Policy --list
```


```bash title="Read a Resource Node"
balcony aws iam Policy

balcony aws ec2 Instances
```


```bash title="Read a Resource Node with --debug enabled"
# if you are curious to see what's going on 
# under the hood, enable the debug messages 
balcony aws iam Policy -d
# or
balcony aws iam Policy --debug
```


```bash title="Read a Resource Nodes specific operation"
balcony aws iam Policy get

balcony aws iam Policy list
```

```bash title="Filter generated parameters with UNIX style pattern matching"
balcony aws iam Policy get  -p "*service-role/*"

# supports multiple patterns 
balcony aws iam Policy -p "*service-role/*" -p "*prod-*"
```


```bash title="Use jmespath queries for the json data"
balcony aws iam Policy \
    --jmespath-selector "GetPolicy[*].Policy"
# or
balcony aws iam Policy \
    -js "GetPolicy[*].Policy"
```


```bash title="Use --format option for customized output"
# create stop-instances script for running instances
balcony aws ec2 Instances \
    -js "DescribeInstances[*].Reservations[*].Instances[?State.Name=='running'][][]" \
    --format "aws ec2 stop-instances --instance-ids {InstanceId} # {Tags}"

# create delete-policy script
balcony aws iam Policy \
    --jmespath-selector "GetPolicy[*].Policy" \
    --format "aws iam delete-policy --policy-arn {Arn}"
```

