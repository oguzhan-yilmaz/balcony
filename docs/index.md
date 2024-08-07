# balcony

balcony is a modern CLI tool that with some killer features:

- Auto-fill the required parameters for AWS API calls
- Read the JSON data of any AWS resource in your account
- Generate [Terraform Import Blocks](https://developer.hashicorp.com/terraform/language/import)
- Generate actual `.tf` Terraform Resource code

balcony uses _read-only_ operations, it does not take any action on the used AWS account.

<!-- ### [**Go to QuickStart Page to get started using _balcony_**](quickstart.md) -->

### Installation

```bash
pip3 install balcony
```

Visit [**Installation & QuickStart Page**](quickstart.md) to get started using _balcony_

```bash  title="Basic usage"
# see options
balcony

# list available resources of ec2
balcony aws ec2 

# read a resource
balcony aws s3 Buckets

# generate terraform import blocks for a resource
balcony terraform-import s3 Buckets
```

## Features

### Read any AWS Resource

Related Docs: [QuickStart](quickstart.md)

!!! tip ""
    ![](visuals/reading-a-resource-node.gif)

---

### Filter and Exclude by Tags

- [aws-jmespath-utils](https://github.com/oguzhan-yilmaz/aws-jmespath-utils) dependency is used to enable JMESPath expressions to filter and exclude resources by tags
- Following expressions are used to select anything: (`=`, `*=`, `=*`, `*=*`)
  - You can leave one side empty or put a `*` there to discard that sides value
-

### Filter tags

- Select everything

  ```bash
  balcony aws ec2 Instances -js 'DescribeInstances[].Reservations[].Instances[].filter_tags(`["="]`, @).Tags'
  balcony aws ec2 Instances -js 'DescribeInstances[].Reservations[].Instances[].filter_tags(`["*="]`, @).Tags'
  balcony aws ec2 Instances -js 'DescribeInstances[].Reservations[].Instances[].filter_tags(`["=*"]`, @).Tags'
  balcony aws ec2 Instances -js 'DescribeInstances[].Reservations[].Instances[].filter_tags(`["*=*"]`, @).Tags'
  ```

- Find named EC2 Instances

  ```bash
  balcony aws ec2 Instances -js 'DescribeInstances[].Reservations[].Instances[].filter_tags(`["Name="]`, @)'
  ```

- Find AWS MAP migration tagged EC2 Instances

  ```bash
  balcony aws ec2 Instances -js 'DescribeInstances[].Reservations[].Instances[].filter_tags(`["map-migrated="]`, @)'
  ```

### Exclude tags

- Exclude everything

  ```bash
  balcony aws ec2 Instances -js 'DescribeInstances[].Reservations[].Instances[].exclude_tags(`["="]`, @).Tags'
  balcony aws ec2 Instances -js 'DescribeInstances[].Reservations[].Instances[].exclude_tags(`["*="]`, @).Tags'
  balcony aws ec2 Instances -js 'DescribeInstances[].Reservations[].Instances[].exclude_tags(`["=*"]`, @).Tags'
  balcony aws ec2 Instances -js 'DescribeInstances[].Reservations[].Instances[].exclude_tags(`["*=*"]`, @).Tags'  
  ```

- Find un-named EC2 Instances

  ```bash
  balcony aws ec2 Instances -js 'DescribeInstances[].Reservations[].Instances[].exclude_tags(`["Name="]`, @)'
  ```

- Find AWS MAP migration un-tagged EC2 Instances

  ```bash
  balcony aws ec2 Instances -js 'DescribeInstances[].Reservations[].Instances[].exclude_tags(`["map-migrated="]`, @)'
  ```

---

### Generate Terraform Import Blocks

Terraform v1.5 introduced [import blocks](https://developer.hashicorp.com/terraform/language/import) that allows users to define their imports as code.

`balcony terraform-import <service> <resource-name>` command generates these import blocks for you.

`balcony terraform-import --list` to see the list of supported resources.

Related Docs: [Generate Terraform Import Blocks](terraform-import.md)
Related Docs: [Balcony Terraform Import Support Matrix](https://oguzhan-yilmaz.github.io/balcony/terraform-import-support-matrix/)

!!! warning ""
    ![](https://raw.githubusercontent.com/oguzhan-yilmaz/balcony-assets/main/gifs/terraform-import-blocks-example.gif)

---

### Generate actual Terraform Resource Code

If you have:

- initialized terraform project
- `import_blocks.tf` file that's generated with `balcony terraform-import` command

you can run `terraform plan -generate-config-out=generated.tf` to generate actual `.tf` resource code.

This feature is achieved with the [balcony-terraform-import Docker Image](https://github.com/oguzhan-yilmaz/balcony/pkgs/container/balcony-terraform-import).

Related Docs: [Generate Terraform Code with Docker Image](terraform-import-docker.md)

!!! info ""
    ![](https://raw.githubusercontent.com/oguzhan-yilmaz/balcony-assets/main/gifs/docker-gen-tf-code-ec2-insances-example.gif)

---

### Interactive Wizard to create balcony import configurations

Balcony doesn't know how to create terraform `import blocks` for all of the AWS resources.

It can be taught how to do it by creating `import-configurations` yaml files, but it's a manual process. This is where the interactive wizard comes in.

Interactive Wizards asks you required questions to automatically create the `import-configurations` yaml files.

Related Docs: [Terraform Import Configuration Wizard](terraform-import-wizard.md)

!!! danger ""

    ![](https://raw.githubusercontent.com/oguzhan-yilmaz/balcony-assets/main/gifs/terraform-wizard-security-groups-example.gif)
