#!/bin/bash

echo "Docker entrypoint script started to run"


terraform version
tf_version_output=$(terraform version)


# Check if the output contains the desired string
if [[ $tf_version_output == *"Your version of Terraform is out of date!"* ]]; then
    echo "TODO: Upgrade the terraform!" # TODO: maybe exit with 1?
# else
#     echo "The output does not contain 'Your version of Terraform is out of date!'"
fi


pip3 show balcony

echo "Using $GEN_TF_DIR directory to save generated terraform files."

echo "Using Terraform AWS provider with profile: $AWS_PROFILE and region: $AWS_DEFAULT_REGION"
bat << EOF >> $GEN_TF_DIR/provider.tf

provider "aws" {
    profile = "$AWS_PROFILE"
    region = "$AWS_DEFAULT_REGION"
}
EOF
echo "--------------------------"
bat  $GEN_TF_DIR/provider.tf
echo "--------------------------"



echo "Running balcony tf-import command to generate import blocks"
# TODO change balcony command
python3 balcony/cli.py tf-import "$@" -o $GEN_TF_DIR/generated_imports.tf

echo "Balcony has generated the following import blocks:"
echo "--------------------------"
bat $GEN_TF_DIR/generated_imports.tf
echo "--------------------------"



pushd $GEN_TF_DIR/
echo "Generating terraform files for import blocks using terraform plan -generate-config-out= command."
terraform plan -generate-config-out=tf_generated.tf

echo "You may see stderr output of terraform above this. It is expected, as the import feature under active development."

echo "Terraform has finished generating the terraform code"
echo "--------------------------"
bat tf_generated.tf
echo "--------------------------"
exit 0