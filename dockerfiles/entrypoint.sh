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



echo "Generating 'provider \"aws\" {}' block in $GEN_TF_DIR/provider.tf file"

if [[ -n "${AWS_PROFILE}" ]]; then
  echo "The AWS_PROFILE environment variable is set to '${AWS_PROFILE}'."
  cat << EOF >> $GEN_TF_DIR/provider.tf

provider "aws" {
    profile   = "$AWS_PROFILE"
    region    = "$AWS_DEFAULT_REGION"
}
EOF


elif [[ -n "${AWS_SESSION_TOKEN}" ]]; then
  # when using a assumed role, there's AWS_SESSION_TOKEN associated with it. Support that.
  echo "The AWS_SESSION_TOKEN environment variable is set to '${AWS_SESSION_TOKEN}'."
  cat << EOF >> $GEN_TF_DIR/provider.tf

provider "aws" {
    access_key  = "$AWS_ACCESS_KEY_ID"
    secret_key  = "$AWS_SECRET_ACCESS_KEY"
    token       = "$AWS_SESSION_TOKEN"
    region      = "$AWS_DEFAULT_REGION"
}
EOF

elif [[ -n "${AWS_ACCESS_KEY_ID}" ]]; then
  echo "The AWS_ACCESS_KEY_ID environment variable is set to '${AWS_ACCESS_KEY_ID}'."
  cat << EOF >> $GEN_TF_DIR/provider.tf

provider "aws" {
    access_key  = "$AWS_ACCESS_KEY_ID"
    secret_key  = "$AWS_SECRET_ACCESS_KEY"
    region      = "$AWS_DEFAULT_REGION"
}
EOF

else
  echo "Neither the AWS_PROFILE nor the AWS_ACCESS_KEY_ID environment variable is set. Please set one of them and rerun the script."
  exit 1
fi



echo "--------------------------"
batcat   $GEN_TF_DIR/provider.tf
echo "--------------------------"



echo "Running balcony terraform-import command to generate import blocks"

python3 balcony/cli.py terraform-import "$@" -o $GEN_TF_DIR/generated_imports.tf

echo "Balcony has generated the following import blocks:"
echo "--------------------------"
batcat  $GEN_TF_DIR/generated_imports.tf
echo "--------------------------"



pushd $GEN_TF_DIR/
echo "Generating terraform files for import blocks using terraform plan -generate-config-out= command."
terraform plan -generate-config-out=tf_generated.tf

echo "You may see stderr output of terraform above this. It is expected, as the import feature under active development."

echo "Terraform has finished generating the terraform code"
echo "--------------------------"
batcat  tf_generated.tf
echo "--------------------------"
exit 0