# balcony

balcony is a Python based CLI tool that simplifies the process of enumerating AWS resources.

balcony dynamically parses `boto3` library and analyzes required parameters for each operation.

By establishing relations between operations over required parameters, it's able to auto-fill them by reading the related operation beforehand.

By simply entering their name, balcony enables developers to easily list their AWS resources.

It uses _read-only_ operations, it does not take any action on the used AWS account.

### [**Go to QuickStart Page to get started using _balcony_**](quickstart.md)

## Features

### List available AWS Services

Use `balcony aws` to see every AWS service available.

![](visuals/aws-services-list.gif)

### List Resource Nodes of an AWS Service

Use `balcony aws <service-name>` to see every Resource Node of a service.

![](visuals/resource-node-list.gif)

### Reading a Resource Node

Use `balcony aws <service-name> <resource-node>` to read operations of a Resource Node.

![](visuals/reading-a-resource-node.gif)

### Documentation and Input & Output of Operations

Use the `--list`, `-l` flag to print the given AWS API Operations documentation, input & output structure.

![--list option gif for balcony project](visuals/list-option.gif)

### Enable Debug messages

Use the `--debug`, `-d` flag to see what's going on under the hood!

![](visuals/debug-messages.gif)
