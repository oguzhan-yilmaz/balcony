# Generate Terraform import blocks with balcony

## Example Recording: ec2 SecurityGroups

![](https://raw.githubusercontent.com/oguzhan-yilmaz/balcony-assets/main/gifs/terraform-import-blocks-example.gif)

## Introduction

Terraform has released version 1.5, and it includes the [import blocks feature](https://developer.hashicorp.com/terraform/language/import) that allows users to define their imports as code. 


This is a great feature that allows you to import existing resources into Terraform and **generate Terraform code** for them.


### What is an import block?

Prior to release of  `v.1.5`, Terraform users had to manually write the Terraform code for existing resources. And then using the `terraform import` command, they could import it into Terraform state.


With the import blocks feature, users can now define their imports as-code, and you can generate the Terraform code for these resources.

```tf title="import_blocks.tf"
# with terraform 1.5+, resources can be imported as-code
import {
  to = aws_instance.example
  id = "i-abcd1234"
}
```



## `balcony terraform-import` command

`balcony terraform-import` command allows you to generate the import blocks for the resources in your AWS account.

```bash title="List which resources can be imported into Terraform"
# print the help screen
balcony terraform-import --help

# list avaliable resource types to import
balcony terraform-import --list
```

!!! Note
    If the resource type you're looking for is not available, you can develop it yourself, locally. Check out the related docs: [Developing Terraform Import Configurations](developing-terraform-import.md). And if you do, please consider contributing it to the project via a PR.


```bash title="Generate import blocks for a resource type in your AWS account"
# Read the first page for ec2 Instances, and generate the import blocks for them
balcony terraform-import ec2 Instances

# paginate through the results, ensuring that all of the resources pages are read
balcony terraform-import ec2 Instances --paginate

# save output to a file
balcony terraform-import ec2 Volumes -p --output /tmp/ec2-volumes-import-blocks.tf
```



## Generating the Actual Terraform Code

First, `cd` into your initialized defined Terraform repo. You should define the AWS Provider Block in your `provider.tf` file.

```bash title="Terraform repo structure"
cd your-terraform-repo/

# it should look like this:
# .
# ├── .terraform/
# ├── .terraform.lock.hcl
# └── provider.tf 
```

After that, we can generate the import blocks for the resource type you want to import. In this case, it's EC2 Instances.

```bash title="Generate Terraform import blocks with balcony"
balcony terraform-import ec2 Instances --paginate -o ec2-instances-import-blocks.tf
```

```bash title="See the generated import blocks"
cat ec2-instances-import-blocks.tf
```

Having the import blocks in our terreform repo, we can generate Terraform code using the `-generate-config-out` option.

```bash title="Generating terraform code using import blocks"
terraform plan -generate-config-out=generated-ec2-instances.tf
```
  
!!! warning "Use Terraform v.1.5+" 
    Make sure to have [Terraform version 1.5+](https://github.com/hashicorp/terraform/releases) installed on your machine. Otherwise, you'll get an error.

When terraform finishes executing, you could see the generated Terraform code in the `generated-ec2-instances.tf` file.

```bash title="Print out the Generated Terraform code"
cat generated-ec2-instances.tf
```

That's it! You can now use the generated Terraform code to manage your existing resources.



You can use balcony terraform-import feature with Docker and generate the Terraform code for it in the container.

!!! Tip "Can I have the actual Terraform code!?"
    Yeah definitely! I've created a Docker image do exactly that.

    See the [relevant docs on how to run balcony terraform-import on Docker](terraform-import-docker.md), create an alias command and use it to generate the **actual Terraform code** for your resources.



**Next Steps**

- [Generating Terraform Code - Official Terraform Documentation](https://developer.hashicorp.com/terraform/language/import/generating-configuration)

- All kinds of resources must have it's own import configuration. This is because each resource has it's own unique import identifier, and it must know which AWS API call to make. 
  You can develop your own import configuration that balcony can understand and serve you with.
  Please check out [Developing Terraform Import Configurations](developing-terraform-import.md)

