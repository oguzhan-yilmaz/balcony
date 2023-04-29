# Developing Custom Resource Nodes

balcony tries it's best to generate the correct relations and API parameters for each operation. But sometimes it's fails to do so.

This is especially true for the operations that have a lot of parameters, and/or the parameters are nested in a complex structure.

In this case, you can define a customized behavior for a resource node to handle the API parameter generation correctly.

balcony provides 2 level of customization for the resource nodes:

## 1. YAML Resource Nodes

You can create a YAML file to alter the behavior of specific ResourceNodes and Operations. Some of the things you can do:

- define explicit relations for specific operations
- override generated api parameters
- complement the generated api parameters (adding/removing parameters)
- provide custom jmepath selector for parameter generation

balcony will automatically register the custom `YamlResourceNode`s defined in the `balcony/custom_yamls/` folder.

## 2. Custom Class Resource Nodes

If the required parameters of an Operation is hard to generate, you can choose to implement parameter generation using custom python classes.


You can create custom python classes that inherit from the `ResourceNode` class. This gives you the full control over the process of reading an operation.

!!! note How balcony loads custom classes for resource nodes 
    balcony has a custom `ResourceNode` subclass registry called `ResourceNodeRegistry`. If the custom class file is under the `balcony/custom_nodes/` folder, and it's exported to `balcony/custom_nodes/__init__.py`, the custom class will be automatically registered to balcony.
    



Either you choose to create a YAML resource node or a Python class resource node, your interception points are the same.

If you can specify explicit relations and get the data you need with only JMESPath, you can use YAML resource nodes. They're easier to write and maintain.

But if you need to implement custom logic to generate the parameters, you can use Python class resource nodes.

## Examples

You can find a documented examples of custom resource nodes in the following files and across the repository:

- **Custom Class Customization**: [custom_nodes/iam.py](https://github.com/oguzhan-yilmaz/balcony/blob/main/balcony/custom_nodes/iam.py)
- **Yaml Customization**: [custom_yamls/iam.yaml](https://github.com/oguzhan-yilmaz/balcony/blob/main/balcony/custom_yamls/iam.yaml)
