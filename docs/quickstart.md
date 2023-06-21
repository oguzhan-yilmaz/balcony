# Quick Start

### Installation

```bash
pip3 install balcony
```

```bash  title="Set your AWS credentials"
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
export AWS_DEFAULT_REGION=us-west-2
```

### Run balcony on Docker

You may choose to [run balcony with Docker](docker.md)

### Shell Autocompletion

=== "Setup for the current shell session"

    ```bash title=""
    balcony --help

    # give your shell as an argument
    balcony --show-completion <your-shell>

    # run the output on your shell to activate the autocompletion
    ```

=== "Setup for your user"

    ```bash
    balcony --help

    # give your shell as an argument
    balcony --install-completion <your-shell>

    # restart your shell
    ```

### About AWS credentials

!!! warning "balcony uses your shell environment for the AWS credentials"

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

### List all available AWS Services

```bash
balcony aws
```

### Remember to get **--help**

```bash
balcony --help
balcony aws --help
```

![balcony --help output screenshot](images/balcony-help.png)


### List all Resource Nodes of a Service

```bash
balcony aws iam

balcony aws ec2
```

### See the documentation of a Resource Node and its Operations

```bash
balcony aws iam Policy -l
# or
balcony aws iam Policy --list
# or to open it on a pager
balcony aws iam Policy -ls
```

### Read a Resource Node

```bash
balcony aws iam Policy

# if you are curious to see what's going on
# under the hood, enable the debug messages
balcony aws iam Policy -d
# or
balcony aws iam Policy --debug
```

### Read a Resource Nodes specific operation

```bash
balcony aws iam Policy get

balcony aws iam Policy list
```

### Use `--paginate`, `-p` option for pagination

Using the `--paginate`, `-p` option allows you to paginate the outputs if they're truncated. If you don't set this flag ==you may get **incomplete data**.==

```bash
# Get all instances available on the AWS Account
balcony aws ec2 Instances \
    -js "DescribeInstances[*].Reservations[*].Instances[]" \
    --paginate --debug
```

### Filter generated parameters with UNIX style `--pattern` matching

!!! note "Important note on **--pattern** option"
    This option only filters the generated api parameters for the given operation.

    Because of this `--pattern` matching is only applied to operations with required parameters.

```bash
balcony aws iam Policy --pattern "*service-role/*"

# supports multiple patterns
balcony aws iam Policy --pattern "*service-role/*" --pattern "*prod-*"
```

### Use JMESPath queries for the json data

You can use [JMESPath](https://jmespath.org/) (like `jq`) to query the output data.

If you are going to use the balcony as a part of your automation scripts, you should use this option to have a more precise output.

```bash
balcony aws iam Policy \
    --jmespath-selector "GetPolicy[*].Policy"
# or
balcony aws iam Policy \
    -js "GetPolicy[*].Policy"
```

### Use `--format` option for customized output

Using the `--format` option allows you to string format the output json data.

Must be used with `-js | --jmespath-selector` option because `--format` option only works with a list of dictionaries of same structure.

Given format string will be applied to each `dict` in the list, allowing you to use [f-strings](https://peps.python.org/pep-0498/) notation.

```bash
# create stop-instances script for running instances
balcony aws ec2 Instances \
    -js "DescribeInstances[*].Reservations[*].Instances[?State.Name=='running'][][]" \
    --format "aws ec2 stop-instances --instance-ids {InstanceId} # {Tags}"

# create delete-policy script
balcony aws iam Policy \
    --jmespath-selector "GetPolicy[*].Policy" \
    --format 'aws iam delete-policy --policy-arn "{Arn}" --version "{DefaultVersionId}"'
```

### Use `--output`, `-o` option for writing the output to a file

Using the `--output`, `-o` option allows you to save the output data to a file.

```bash
# Get all instances available on the AWS Account
balcony aws ec2 Instances \
    -js "DescribeInstances[*].Reservations[*].Instances[]" \
    --paginate --debug \
    --output /tmp/balcony-output.json
```
