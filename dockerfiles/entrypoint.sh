#!/bin/bash
function debug_echo {
  if [[ $BALCONY_DEBUG -eq 1 ]]; then
    echo "$@"
  fi
}

debug_echo "Docker entrypoint script started to run"

# Create an empty string to store the filename
gen_terraform_filename=""



# Iterate over all arguments to generate the generated terraform filename
for arg in "$@"
do
    # If the gen_terraform_filename is not empty, append a hyphen before adding the new argument
    if [ ! -z "$gen_terraform_filename" ]; then
        gen_terraform_filename+="-"
    fi
    # Append the argument to the gen_terraform_filename
    gen_terraform_filename+="$arg"
done

# Append the .tf extension
gen_terraform_filename+=".tf"
gen_terraform_import_blocks_filename="import-blocks-${gen_terraform_filename}"

# Print the gen_terraform_filename
debug_echo "Generated gen_terraform_filename: $gen_terraform_filename"


if [[ $# -lt 1 ]] || [[ $# -gt 2 ]]; then
    echo "\n ERROR: This script has two arguments types:"
    echo "\t Option 1. [service, resource_name](e.g. ec2 Instances, iam Users)": 
    echo "\t Option 2. [terraform_resource_type](e.g. aws_instance, aws_iam_user)"
    exit 1
fi


if [[ $BALCONY_DEBUG -eq 1 ]]; then
  echo "Debugging mode is enabled."

  set -x
  tf_version_output=$(terraform version)
  echo ""


  if [[ $tf_version_output == *"Your version of Terraform is out of date!"* ]]; then
      echo "TODO: Upgrade the terraform!" # TODO: maybe exit with 1?
  fi

  pip3 show balcony
  echo ""
fi


# debug_echo "Upgrading the balcony package to the latest version."
# PIP_DISABLE_PIP_VERSION_CHECK=1
# pip3 install --upgrade --no-python-version-warning --disable-pip-version-check --no-input -q balcony

debug_echo "Using $GEN_TF_DIR directory to save generated terraform files."

# ------ Generate provider "aws" block to provider.tf file

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
echo "The AWS_DEFAULT_REGION environment variable is set to '${AWS_DEFAULT_REGION}'."

echo "Running balcony terraform-import command to generate import blocks"
balcony terraform-import "$@" --paginate -o $GEN_TF_DIR/$gen_terraform_import_blocks_filename

# check if the file is generated or not
if [[ -f $GEN_TF_DIR/$gen_terraform_import_blocks_filename ]]; then
  echo "File $GEN_TF_DIR/$gen_terraform_import_blocks_filename exists."
  echo "Balcony has generated the following import blocks:"
  echo "-------$gen_terraform_import_blocks_filename-----------"
  cat  $GEN_TF_DIR/$gen_terraform_import_blocks_filename
  cp $GEN_TF_DIR/$gen_terraform_import_blocks_filename /balcony-output
  echo "------------------------------------"

else
  echo "Balcony failed to generate the import blocks. Running the same command in debug mode."
  balcony terraform-import --debug "$@" 
  echo "Please check the debug output above to see what went wrong."
  echo "Exiting..."
  exit 1
fi





pushd $GEN_TF_DIR/ > /dev/null
debug_echo "Generating terraform files for import blocks using terraform plan -generate-config-out= command."
terraform plan -generate-config-out=$gen_terraform_filename

echo "^^^^^^^^^^^^^^^^^^^^^^^^^^"
echo "You may see stderr output of terraform above this. It is expected, as the import feature under active development."

debug_echo "Terraform has finished generating the terraform code"
echo "---------$gen_terraform_filename-----------"
cat $gen_terraform_filename
cp $gen_terraform_filename  /balcony-output 

if [[ $BALCONY_DEBUG -eq 1 ]]; then
  # cleanup
  set +x
fi

exit 0