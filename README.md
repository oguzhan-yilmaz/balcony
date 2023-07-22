# balcony


<div style="display: flex;">
  <a href="https://github.com/oguzhan-yilmaz/balcony/actions/workflows/docker-publish.yml"><img src="https://github.com/oguzhan-yilmaz/balcony/actions/workflows/docker-publish.yml/badge.svg" alt="Build and publish a Docker image to ghcr.io"></a>
  <span style="width: 5px"></span>

<a href="https://github.com/oguzhan-yilmaz/balcony/actions/workflows/pages/pages-build-deployment"><img src="https://github.com/oguzhan-yilmaz/balcony/actions/workflows/pages/pages-build-deployment/badge.svg" alt="Build and Deploy Documentation website"></a>
</div>


balcony is a modern CLI tool that with some killer features:

- Auto-fill the required parameters for AWS API calls 
- Read the JSON data of any AWS resource in your account
- Generate [Terraform Import Blocks](https://developer.hashicorp.com/terraform/language/import)
- Generate actual `.tf` Terraform Resource code

balcony uses _read-only_ operations, it does not take any action on the used AWS account.


### [Visit the Documentation Website](https://oguzhan-yilmaz.github.io/balcony/quickstart/)
<!-- ### [**Go to QuickStart Page to get started using _balcony_**](quickstart.md) -->

### Installation

```bash
pip3 install balcony
```

Visit [**Installation & QuickStart Page**](https://oguzhan-yilmaz.github.io/balcony/quickstart/) to get started using _balcony_

```bash  title="Basic usage"
# see options
balcony

# list available resources of ec2
balcony aws ec2 

# read a resource
balcony aws s3 Buckets

# show documentation
balcony aws iam Policy --list

# generate terraform import blocks for a resource
balcony terraform-import s3 Buckets
```


## Features

### Read any AWS Resource

`balcony aws <service> <resource-name> --paginate` command reads all resources of a given type in your AWS account.

Related Docs: [QuickStart](https://oguzhan-yilmaz.github.io/balcony/quickstart/)

![](https://raw.githubusercontent.com/oguzhan-yilmaz/balcony-assets/main/gifs/aws-read-resource.gif)


---

### Generate Terraform Import Blocks

Terraform v1.5 introduced [import blocks](https://developer.hashicorp.com/terraform/language/import) that allows users to define their imports as code.

`balcony terraform-import <service> <resource-name>` command generates these import blocks for you.

`balcony terraform-import --list` to see the list of supported resources.

Related Docs: [Generate Terraform Import Blocks](https://oguzhan-yilmaz.github.io/balcony/terraform-import/)
Related Docs: [Balcony Terraform Import Support Matrix](https://oguzhan-yilmaz.github.io/balcony/terraform-import-support-matrix/)



![](https://raw.githubusercontent.com/oguzhan-yilmaz/balcony-assets/main/gifs/terraform-import-blocks-example.gif)


---

### Generate actual Terraform Resource Code 


If you have:

- initialized terraform project
- `import_blocks.tf` file that's generated with `balcony terraform-import` command

you can run `terraform plan -generate-config-out=generated.tf` to generate actual `.tf` resource code.

This feature is achieved with the [balcony-terraform-import Docker Image](https://github.com/oguzhan-yilmaz/balcony/pkgs/container/balcony-terraform-import).


Related Docs: [Generate Terraform Code with Docker Image](https://oguzhan-yilmaz.github.io/balcony/terraform-import-docker/)

![](https://raw.githubusercontent.com/oguzhan-yilmaz/balcony-assets/main/gifs/docker-gen-tf-code-ec2-insances-example.gif)


---

### Interactive Wizard to create balcony import configurations 

Balcony doesn't know how to create terraform `import blocks` for all of the AWS resources.

It can be taught how to do it by creating `import-configurations` yaml files, but it's a manual process. This is where the interactive wizard comes in.

Interactive Wizards asks you required questions to automatically create the `import-configurations` yaml files.

Related Docs: [Terraform Import Configuration Wizard](https://oguzhan-yilmaz.github.io/balcony/terraform-import-wizard/)

![](https://raw.githubusercontent.com/oguzhan-yilmaz/balcony-assets/main/gifs/terraform-wizard-security-groups-example.gif)
