# 🏡 Balcony: Your AWS CLI Companion for Cloud Resource Insight & Terraform Generation

[![Build and publish a Docker image to ghcr.io](https://github.com/oguzhan-yilmaz/balcony/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/oguzhan-yilmaz/balcony/actions/workflows/docker-publish.yml)
[![Build and Deploy Documentation website](https://github.com/oguzhan-yilmaz/balcony/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/oguzhan-yilmaz/balcony/actions/workflows/pages/pages-build-deployment)
[![PyPI](https://img.shields.io/pypi/v/balcony)](https://pypi.org/project/balcony/)
[![License](https://img.shields.io/github/license/oguzhan-yilmaz/balcony)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/oguzhan-yilmaz/balcony?style=social)](https://github.com/oguzhan-yilmaz/balcony/stargazers)

`balcony` is a modern, feature-rich command-line interface (CLI) tool designed to simplify your interactions with AWS. It provides unparalleled visibility into your cloud resources and dramatically accelerates your Infrastructure as Code (IaC) workflows by generating Terraform import blocks and even complete Terraform resource configurations.

Built with Python 🐍, `typer` ✨, and `boto3` ⚙️, `balcony` offers a read-only perspective on your AWS environment, ensuring safe exploration and powerful automation capabilities without making any changes to your infrastructure.

---

## ✨ Features

*   **🔍 AWS Resource Discovery**: Effortlessly list and read the JSON data of any AWS resource in your account.
*   **🎯 Smart Parameter Auto-fill**: `balcony` intelligently identifies and auto-fills required parameters for AWS API calls, saving you time and reducing errors.
*   **🏷️ Tag-based Filtering**: Leverage JMESPath expressions to precisely filter and exclude AWS resources by their tags.
*   **🏗️ Terraform Import Block Generation**: Automatically generate `import` blocks for existing AWS resources, adhering to Terraform v1.5+ standards.
*   **🔄 Terraform Resource Code Generation**: Go beyond import blocks! Utilize `balcony`'s specialized Docker image to generate actual `.tf` Terraform resource configurations from your live AWS resources.
*   **🧙 Interactive Configuration Wizard**: Create custom Terraform import configurations with an intuitive, interactive wizard, making `balcony` adaptable to your specific IaC needs.
*   **⚡ Blazing Fast**: Optimized for speed and efficiency, giving you quick insights and generations.

---

## 🚀 Quick Start

Get `balcony` up and running in minutes!

### Installation

```bash
pip3 install balcony
```

### Basic Usage

Explore your AWS resources and start generating Terraform configurations.

1.  **List Available Services & Resources**:
    ```bash
    # See all available AWS services
    balcony aws

    # List resources for a specific service, e.g., EC2
    balcony aws ec2
    ```

2.  **Read an AWS Resource**:
    ```bash
    # Read all S3 buckets in your account
    balcony aws s3 Buckets --paginate -p

    # Read EC2 instances and filter by a JMESPath selector
    balcony aws ec2 Instances -js 'DescribeInstances[].Reservations[].Instances[].{InstanceId: InstanceId, State: State.Name, Tags: Tags}'
    ```

3.  **Generate Terraform Import Blocks**:
    ```bash
    # Generate import blocks for S3 Buckets
    balcony terraform-import s3 Buckets -o import_s3_buckets.tf

    # List all supported resources for Terraform import
    balcony terraform-import --list
    ```

4.  **Generate Terraform Resource Code with Docker**:
    (Requires Docker installed)

    First, generate import blocks (e.g., `import_s3_buckets.tf`). Then, use the `balcony-terraform-import` Docker image:

    ```bash
    # Example: Assuming you have import_s3_buckets.tf in your current directory
    docker run --rm -v $(pwd):/terraform-app -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION ghcr.io/oguzhan-yilmaz/balcony-terraform-import:latest plan -generate-config-out=generated.tf

    # This will create a 'generated.tf' file with the Terraform resource code.
    ```

---

## 📖 Documentation

For in-depth guides, advanced usage, and development insights, visit our comprehensive documentation website:

[**oguzhan-yilmaz.github.io/balcony/quickstart/**](https://oguzhan-yilmaz.github.io/balcony/quickstart/)

---

## 🤝 Contributing

We welcome contributions! Whether it's reporting bugs, suggesting features, or submitting pull requests, your help makes `balcony` better. Please refer to our [Contributing Guidelines](https://github.com/oguzhan-yilmaz/balcony/blob/main/.github/CONTRIBUTING.md) (TODO: Create this file) for more details.

---

## 📄 License

`balcony` is open-source software licensed under the [Apache-2.0 License](LICENSE).

---

## 📞 Support & Community

*   **GitHub Issues**: For bug reports and feature requests, please use the [GitHub Issue Tracker](https://github.com/oguzhan-yilmaz/balcony/issues).
*   **Discussions**: Join our [GitHub Discussions](https://github.com/oguzhan-yilmaz/balcony/discussions) (TODO: Enable Discussions) for questions, ideas, and general conversations.
*   **Twitter**: Follow [@oguzhan_y_](https://twitter.com/oguzhan_y_) for updates.
