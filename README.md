# balcony

balcony is a Python based CLI tool that simplifies the process of enumerating AWS resources.

balcony dynamically parses `boto3` library and analyzes required parameters for each operation. 

By establishing relations between operations over required parameters, it's able to auto-fill them by reading the related operation beforehand.

By simply entering their name, balcony enables developers to easily list their AWS resources.

It uses _read-only_ operations, it does not take any action on the used AWS account.

### [Go to Documentation Website](https://oguzhan-yilmaz.github.io/balcony/quickstart)

## Features

### List available AWS Services 
Use `balcony aws` to see every AWS service available.

![](https://github.com/oguzhan-yilmaz/balcony/blob/main/docs/visuals/aws-services-list.gif)


### List Resource Nodes of an AWS Service 
Use `balcony aws <service-name>` to see every Resource Node of a service.

![](https://github.com/oguzhan-yilmaz/balcony/blob/main/docs/visuals/resource-node-list.gif)


### Reading a Resource Node 
Use `balcony aws <service-name> <resource-node>` to read operations of a Resource Node.

![](https://github.com/oguzhan-yilmaz/balcony/blob/main/docs/visuals/reading-a-resource-node.gif)


### Documentation and Input & Output of Operations
Use the `--list`, `-l` flag to print the given AWS API Operations documentation, input & output structure. 
 

![](https://github.com/oguzhan-yilmaz/balcony/blob/main/docs/visuals/list-option.gif)


### Enable Debug messages 
Use the `--debug`, `-d` flag to see what's going on under the hood!

![](https://github.com/oguzhan-yilmaz/balcony/blob/main/docs/visuals/debug-messages.gif)
