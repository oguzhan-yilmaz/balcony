# Terraform Import Wizard

Interactive tool to generate balcony terraform `import-configurations`.
## Example Recording: ec2 SecurityGroups 
![](https://raw.githubusercontent.com/oguzhan-yilmaz/balcony-assets/main/gifs/terraform-wizard-security-groups-example.gif)

## About balcony terraform import-configurations


Balcony can generate import blocks for terraform resources if it knows how to do so.

We can let balcony know how to generate import blocks by creating a `.yaml` file, that looks like this:

```yaml title="Example terraform import-configuration .yaml file"
import_configurations:
  - service: ec2
    resource_node: Instances
    operation_name: DescribeInstances
    to_resource_type: aws_instance
    jmespath_query: "[].Reservations[].Instances[]"
    to_resource_name_jinja2_template: "{{ tag_Name or InstanceId }}"
    id_generator_jinja2_template: "{{ InstanceId }}"
```

Related docs: [About Terraform Import Configurations](about-terraform-import.md)

---
## About the Wizard


`balcony terraform-wizard` is an **interactive command** that helps you generate the `import-configurations` yaml files.

It asks you questions about the resource you want to import. And validates your answers with confirmation.

This makes it very easy to try and find out the correct configuration for your resource.


!!! Tip "Act of Development might require some reading"

    Please read the related docs before using this feature: 
    
    - [About Terraform Import Configurations](about-terraform-import.md)
    - [Generate Terraform import blocks](terraform-import.md)

    And check out example configurations: [Github: balcony/custom_tf_import_configs/*.yaml](https://github.com/oguzhan-yilmaz/balcony/tree/main/balcony/custom_tf_import_configs)




### Get started


```bash title="List command options"
balcony terraform-wizard
```

---

## Example: EC2 SecurityGroups

This


### Operation Selection

```bash title="List command options"
Select which operation [DescribeSecurityGroups] (DescribeSecurityGroups):
```


### 


































