# Quick Start
### Installation

```bash
pip3 install balcony
```
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



!!! note "Remember to get **--help**" 

    ```bash  title=""
    balcony --help
    balcony aws --help
    ```

### List all available AWS Services

```bash
balcony aws
```
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

### Filter generated parameters with UNIX style `--pattern` matching
!!! note "Important note on **--pattern** option" 
    This option only filters the generated api parameters for the given operation.

    Because of this `--pattern` matching is only applied to operations with requried parameters.
    

```bash
balcony aws iam Policy get  -p "*service-role/*"

# supports multiple patterns 
balcony aws iam Policy -p "*service-role/*" -p "*prod-*"
```

### Use JMESPath queries for the json data

You can use [JMESPath](https://jmespath.org/) (like `jq`) to query the output data.

```bash
balcony aws iam Policy \
    --jmespath-selector "GetPolicy[*].Policy"
# or
balcony aws iam Policy \
    -js "GetPolicy[*].Policy"
```

### Use `--format` option for customized output

Using the `--format` option allows you to string format the output json data.

Must be used with `-js | --jmespath-selector` option because `--format` option only works with a list of dictionaries.

Given format string will be applied to each `dict` in the list, allowing you to use [f-strings](https://peps.python.org/pep-0498/) notation. 

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