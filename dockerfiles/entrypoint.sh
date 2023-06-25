#!/bin/bash
function debug_echo {
  if [[ $BALCONY_DEBUG -eq 1 ]]; then
    echo "$@"
  fi
}

debug_echo "Docker entrypoint script started to run"

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

debug_echo "Upgrading the balcony package to the latest version."
pip3 install --upgrade --no-input -q balcony

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

# ------ Generate provider "aws" block to provider.tf file

echo "--------------------------"
cat   $GEN_TF_DIR/provider.tf
echo "--------------------------"



echo "Running balcony terraform-import command to generate import blocks"

balcony terraform-import "$@" -o $GEN_TF_DIR/generated_imports.tf

# check if the file is generated or not
if [[ -f $GEN_TF_DIR/generated_imports.tf ]]; then
  echo "File $GEN_TF_DIR/generated_imports.tf exists."
  echo "Balcony has generated the following import blocks:"
  echo "--------------------------"
  cat  $GEN_TF_DIR/generated_imports.tf
  cp $GEN_TF_DIR/generated_imports.tf /balcony-output
  echo "--------------------------"

else
  echo "Balcony failed to generate the import blocks. Running the same command in debug mode."
  balcony terraform-import --debug "$@" 
  echo "Please check the debug output above to see what went wrong."
  echo "Exiting..."
  exit 1
fi





pushd $GEN_TF_DIR/
debug_echo "Generating terraform files for import blocks using terraform plan -generate-config-out= command."
terraform plan -generate-config-out=tf_generated.tf

echo "You may see stderr output of terraform above this. It is expected, as the import feature under active development."

debug_echo "Terraform has finished generating the terraform code"
echo "--------------------------"
cat  tf_generated.tf
cp tf_generated.tf /balcony-output 

if [[ $BALCONY_DEBUG -eq 1 ]]; then
  # cleanup
  set +x
fi

exit 0