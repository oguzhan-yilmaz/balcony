#!/bin/bash

function debug_echo {
  if [[ $BALCONY_DEBUG -eq 1 ]]; then
    if [[ -p /dev/stdin ]]; then
      while IFS= read -r line
      do
        echo "$line"
      done
    else
      echo "$@"
    fi
  fi
}

debug_echo "Docker entrypoint script started to run"


debug_echo "Printing the terraform version"
terraform version | debug_echo
debug_echo ""

tf_version_output=$(terraform version)


# Check if the output contains the desired string
if [[ $tf_version_output == *"Your version of Terraform is out of date!"* ]]; then
    echo "TODO: Upgrade the terraform to new version!" # TODO: maybe exit with 1?
fi

debug_echo "Printing the balcony version"
pip3 show balcony | debug_echo
balcony info | debug_echo

debug_echo "Using $GEN_TF_DIR directory to save generated terraform files."


debug_echo "Generating 'provider \"aws\" {}' block in $GEN_TF_DIR/provider.tf file"

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
batcat  $GEN_TF_DIR/provider.tf
echo "--------------------------"



debug_echo "Running balcony terraform-import command to generate import blocks"

balcony terraform-import "$@" -o $GEN_TF_DIR/generated_imports.tf

debug_echo "Balcony has generated the following import blocks:"
echo "--------------------------"
batcat  $GEN_TF_DIR/generated_imports.tf
echo "--------------------------"



pushd $GEN_TF_DIR/
debug_echo "Generating terraform files for import blocks using terraform plan -generate-config-out= command."
terraform plan -generate-config-out=tf_generated.tf

echo "--------------------------"
echo "You may see stderr output of terraform above this. It is expected, as the import feature under active development."

debug_echo "Terraform has finished generating the terraform code"
echo "--------------------------"
batcat  tf_generated.tf
echo "--------------------------"
debug_echo "Script has finished. Exiting successfully."

exit 0