# Yaml Resource Nodes

You can create a YAML file to alter the behavior of specific ResourceNodes and Operations. 

!!! important "Complete YAML example"
    Check out the documented YAML file: [balcony/custom_yamls/_example_service.yaml](https://github.com/oguzhan-yilmaz/balcony/blob/main/balcony/custom_yamls/_example_service.yaml) in the repository.


## YAML Structure


Custom YAML files are defined in the `custom_yamls/` folder and picked up by balcony automatically.

balcony uses `pydantic` for configuration input validation, and apart from `service_name` and `resource_node_name` all other keys are optional. 

The custom yaml file should be in the following format:


```yaml title="balcony/custom_yamls/_example_service.yaml"
# This is an example config for customizing behaviors of Resource Nodes.
# Almost all features you can define are **optional**, define what you need.
# It's advised to check out other .yaml files.
service_name: <service-name> # AWS Service short name
resource_nodes:
- resource_node_name: <resource-node-name> # non-optional
  # rest of this level keys are all optional 
  extra_relations: 
    # extra_relations will be visible to the current and all other 
    # operations in this Service. Use this feature to add a missing 
    # Relation that can also benefit other operations.
    - service_name: <> 
      resource_node_name: <> 
      operation_name: <>
      required_shape_name: <> 
      target_shape_name: <>
      target_shape_type: <>
      target_path: <>
  operations:
    # Operation level customization must define a specific `operation_name` 
    - operation_name: <operation-name> 
      # Pagination token mapping customization
      pagination_token_mapping:
        output_key: NextContinuationToken # from output, get this key and
        parameter_name: ContinuationToken # pass it to this parameter
      # This option overrides the `complement_api_parameters_list` function.
      complement_api_parameters:
        # This option will be evoked after api parameter generation is 
        # complete. You can use this feature to add key/value pairs, 
        - action: add
          data:
            any: data
            is: fine
            to: add
        #  or remove keys from all generated API parameters.
        - action: remove
          keys:
            - remove
            - these
            - keys
      # This option overrides the `generate_jmespath_selector_from_relations`.
      jmespath_selector: <jmespath-selector>
      # This operation will be called with all of it's related operations 
      # defined in the Relations. You can craft a jmespath selector query 
      # to extract the api parameters list. Adviced to be used with 
      # `explicit_relations` feature.

      # This option overrides the `get_operations_relation` function.
      explicit_relations:
        # You can define explicit relations for this specific operation.
        # If you are going to also provide `jmespath_selector` option in 
        #   this yaml, you don't need to specify anthing other than service, 
        #   resource and operation name.
        # All the `operation_name`s you define in explicit_relations, will 
        #   be called before reading the current operation. Use both features 
        #   to request related operations data and extract api parameters from it. 
        - service_name: <>
          resource_node_name: <> 
          operation_name: <>
          required_shape_name: <> 
          target_shape_name: <>
          target_shape_type: <>
          target_path: <>
      # This option overrides the `generate_api_parameters_from_operation_data`
      override_api_parameters:
        # The function will only be called with the list of dicts you define here.
        # This will bypass jmespath_selector and jmespath_selector features.
        - set: static
          params: for
          this: operation
```
