#!/bin/bash

# info logs the given argument at info log level.
info() {
    echo "[INFO] " "$@"
}

# warn logs the given argument at warn log level.
warn() {
    echo "[WARN] " "$@" >&2
}

# fatal logs the given argument at fatal log level.
fatal() {
    echo "[ERROR] " "$@" >&2
    exit 1
}

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
batcat -P -p  << EOF >> $GEN_TF_DIR/provider.tf

provider "aws" {
    profile = "$AWS_PROFILE"
    region = "$AWS_DEFAULT_REGION"
}
EOF
echo "--------------------------"
batcat -P -p   $GEN_TF_DIR/provider.tf
echo "--------------------------"



echo "Running balcony terraform-import command to generate import blocks"

python3 balcony/cli.py terraform-import "$@" -o $GEN_TF_DIR/generated_imports.tf

echo "Balcony has generated the following import blocks:"
echo "--------------------------"
batcat -P -p  $GEN_TF_DIR/generated_imports.tf
echo "--------------------------"



pushd $GEN_TF_DIR/
echo "Generating terraform files for import blocks using terraform plan -generate-config-out= command."
terraform plan -generate-config-out=tf_generated.tf

echo "You may see stderr output of terraform above this. It is expected, as the import feature under active development."

echo "Terraform has finished generating the terraform code"
echo "--------------------------"
batcat -P -p  tf_generated.tf
echo "--------------------------"
exit 0