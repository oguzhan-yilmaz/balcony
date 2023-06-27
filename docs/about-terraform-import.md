# Developing Balcony terraform import configurations for AWS resources 

This document details the process of developing Terraform import configurations for balcony.


!!! Tip 
    You can define your own configurations on a local folder that you have, and they'll be loaded to balcony. You just have to set an environment variable.

    ```bash 
    export BALCONY_TERRAFOM_IMPORT_CONFIG_DIR=$HOME/balcony-tf-yamls
    ```

    Allowing you to add/override import configurations. 

### What is an import block?

Prior to release of  `v.1.5`, Terraform users had to manually write the Terraform code for existing resources. And then using the `terraform import` command, they could import it into Terraform state.


With the import blocks feature, users can now define their imports as-code, and Terraform will generate the Terraform code for the resource.

```hcl title="import_blocks.tf"
# with terraform 1.5+, resources can be imported as-code
import {
  to = aws_instance.example
  id = "i-abcd1234"
}
```

[See the relevant docs page for more details](terraform-import.md)


!!! Note
    - Not all resources can be imported into Terraform.
        [AWS Terraform Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs) must be checked for each resource type.
    - Each resource type has a different `import ID format` 
        For example, [aws_volume_attachment](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/volume_attachment) has import ID format of `DEVICE_NAME:VOLUME_ID:INSTANCE_ID`)
    
     

This means that in order to generate Terraform code for a resource, you'll need to have:

- `terraform type` and `name` of the resource that'll be used to generate the Terraform code for
- the resource ID that'll be used to import the resource (which is different for each resource type)

### This is great, but...

Having to figure out the suitable `resource name` and `import ID` for each resource is still some work.

And doing this for all of the resources in your AWS account is **a lot of** work.

### Let's automate this

With [balcony](https://github.com/oguzhan-yilmaz/balcony), we already have the capability to read/list any AWS resource. So we can get the JSON data of any resource in an AWS account.


Using this data, we'd need to figure out how to generate:

- `import ID format` for this type of resource
- how to name it, so it's unique in the generated Terraform code 


Since the `import ID format` is different for each resource type, we'd need a way to generate it for each resource type.

Instead of doing this in the source code, one by one, tediously... We can use a configuration file to define how to generate the `import block` for each resource type.

### Creating the framework for generating Terraform import blocks

We need to bind the AWS Resource Types to how they'd be written as Terraform `import blocks`


Let's take the example of AWS EC2 Instance, or `aws_instance` resource type, and figure out what we need to generate the `import block`.


**Which AWS API Operation should be called to fetch the data?**

We are using balcony to fetch the data, so we need to know which AWS API Operation to call. In this case, it's `DescribeInstances`.

Our config must include this information:

```yaml
service: ec2
resource_node: Instances
operation_name: DescribeInstances
```


You can see the data you'd get using the `balcony aws ec2 Instances describe` command, which would read the Describe operation specifically.

To see the Operations of a ResourceNode, you can use the  `--list, -l` option. (e.g. `balcony aws ec2 Instances --list`). This will bring up the Operations and their documentation.

**Which Terraform to resource type it should use?**

We know `aws_instance` is the resource type for EC2 Instances [from the Terraform AWS prodiver docs.](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance)

Let's add this to our config:

```yaml
to_resource_type: aws_instance
```


**How should the data be filtered?**

The data returned by the AWS API Operation is usually a JSON. We need to filter this data to get the list of resources we want to generate Terraform code for.

This is especially important because we are using balcony, **which returns the collection of responses it got from the AWS API Operation**. So we definitely need to filter the data using [JMESPath](https://jmespath.org/) data query selectors.


```yaml
jmespath_query: "[].Reservations[].Instances[]"
```

Here we select from all of the responses, the `Reservations` key, and then the `Instances` key from each of the `Reservations`. This query will result in a _concise list of EC2 Instances_, allowing us to generate Terraform code for each of them in a loop.



!!! important 
    If you fill in the `jmespath_query` option, jinja2 templates will be evaluated in the context of the selected data. This means that you don't have to loop over the data, and just access the attrs.

    

**How should the `import ID` be generated?**

We need a way to allow users to define templates, so [Jinja2](https://jinja.palletsprojects.com/) is selected as the templating engine.

We're passing all of the data we got from the AWS API Operation to the Jinja2 template as the variable `data`.
And if the `jmespath_query` is used, we're calling the template in a loop, and the current items attributes are directly accessible by their names.


```yaml
id_generator_jinja2_template: "{{ InstanceId }}"
```

**How should the terraform resource name be generated?**

It's important to generate a unique name for each resource, so that the generated Terraform code is valid.


If there're tags defined in the resource data, you can access them by prefixing their name with `tag_`.

AWS manages their resource namings as tags, so it's handy to have direct access to `tag_Name`.

```yaml
to_resource_name_jinja2_template: "{{ tag_Name or InstanceId }}"
```

This template will get the Name tag if available, or it'll default to `InstanceId`.

### Putting it all together

We can have a configuration file that looks like this:


```yaml title="ec2.yaml"
import_configurations:
  - service: ec2
    resource_node: Instances
    operation_name: DescribeInstances
    to_resource_type: aws_instance
    jmespath_query: "[].Reservations[].Instances[]"
    to_resource_name_jinja2_template: "{{ tag_Name or InstanceId }}"
    id_generator_jinja2_template: "{{ InstanceId }}"

  - service: ec2
    resource_node: Volumes
    operation_name: DescribeVolumes
    to_resource_type: aws_ebs_volume
    jmespath_query: "[].Volumes[]"
    to_resource_name_jinja2_template: "{{ VolumeId }}"
    id_generator_jinja2_template: "{{ VolumeId }}"
```


Balcony has a special directory `balcony/custom_tf_import_configs/` for terraform import configurations, and it'll automatically load any `.yaml` file.


Besides from this directory, you can set the `BALCONY_TERRAFOM_IMPORT_CONFIG_DIR` Environment Variable to point to a directory that contains your import configurations. Your configurations will override the default ones balcony provide.

```bash title="Setting the custom terraform import config .yaml directory"
# create the directory
mkdir -p $HOME/balcony-tf-yamls

# set the custom terraform import config directory
export BALCONY_TERRAFOM_IMPORT_CONFIG_DIR=$HOME/balcony-tf-yamls
```




I encourage you to contribute and create PRs for your favorite AWS resources. Peace!
