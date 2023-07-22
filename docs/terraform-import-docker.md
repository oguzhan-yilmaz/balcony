# balcony terraform-import on Docker


`balcony terraform-import` command allows us to get the import blocks for the resources in our AWS account.

But it's still not generating the actual Terraform code for us. Let's fix that.

## Example Recording: ec2 Insances
![](https://raw.githubusercontent.com/oguzhan-yilmaz/balcony-assets/main/gifs/docker-gen-tf-code-ec2-insances-example.gif)

## Docker Image

- Github Container Registry: [balcony-terraform-import](https://github.com/oguzhan-yilmaz/balcony/pkgs/container/balcony-terraform-import)

- Dockerfile: [terraform-import.Dockerfile](https://github.com/oguzhan-yilmaz/balcony/blob/main/dockerfiles/terraform-import.Dockerfile)

```bash title="Pull the balcony-terraform-import image"
docker pull ghcr.io/oguzhan-yilmaz/balcony-terraform-import:main
```

This Docker image installs `balcony` and `terraform v.1.5+` on top of the base image.

It also copies over 2 files to image:

- `provider.tf`: Used for `terraform init`ialization on image build-time.
- `entrypoint.sh`: Bash script for running `balcony terraform-import` and `terraform plan -gen-generate-config-out=`.



## How to use the `balcony-terraform-import` Docker image

Our Docker image has a lot of options, so it's handy to create an `alias` command for it.

There're multiple ways of providing these options. First, let's walk through the options.

## Docker run Options

Following are docker run options for providing 

- AWS Credentials to the container,
- (optional) defining a directory to save the generated files,
- (optional) and enabling container debug messages

to the container.

### Option: AWS Credentials


**1. Mounting your AWS Credential Folder `~/.aws/`**

If you use `AWS CLI`, you can mount your `~/.aws/` folder to the container.

You'd also need to set the `AWS_PROFILE` and `AWS_DEFAULT_REGION` environment variables to select from your credential files.


```bash title="Docker options for mounting ~/.aws/ folder to container"
  -v ~/.aws:/root/.aws \
  -e AWS_PROFILE="default" \
  -e AWS_DEFAULT_REGION="eu-west-1" \
```

**2. Directly giving the AWS Credentials in Env Vars**

You can also directly provide the AWS Credentials in environment variables.

```bash title="AWS Credentials in Environment Variables"
  -e AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE" \
  -e AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" \
  -e AWS_DEFAULT_REGION="eu-west-1" \
```

**3. Directly giving the Assumed Role AWS Credentials in Env Vars**

You can also directly provide an Assumed Role AWS Credentials in environment variables.

The difference is you also provide the `AWS_SESSION_TOKEN` environment variable.

```bash title="AWS Credentials in Environment Variables"
  -e AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE" \
  -e AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" \
  -e AWS_SESSION_TOKEN="wasfjoAfn21ALfj/bPxRfiCYEXAMPLE-SESSION-TOKEN" \
  -e AWS_DEFAULT_REGION="eu-west-1" \
```

### Option: Output Directory

Docker image will use `/balcony-output` as the default output directory. 

You can mount a folder you have as a volume to the container. This way you'll get the files in your local machine.

```bash
  -v $BALCONY_TF_GEN_OUTPUT_DIR:/balcony-output \
```
We can achieve by providing the docker run with `-v <your-directory>:/balcony-output`

You can also copy the output from the terminal window if you don't use this option.

## Alias Commands

You can copy these alias commands to your `~/.bashrc` or `~/.zshrc` file to persist them.

```bash title="Alias with ~.aws/ folder mounted"
# set your options here
BALCONY_AWS_PROFILE="hepapi"
BALCONY_AWS_DEFAULT_REGION="eu-central-1"
BALCONY_TF_GEN_OUTPUT_DIR="/tmp/balcony-terraform-gen"
BALCONY_DEBUG=0

# create the alias command, with your options
alias balcony-tf-import="mkdir -p $BALCONY_TF_GEN_OUTPUT_DIR \
    && docker pull ghcr.io/oguzhan-yilmaz/balcony-terraform-import:main \
    && echo \"Generated files will be saved to: $BALCONY_TF_GEN_OUTPUT_DIR\n\" \
    && docker run \
        -v ~/.aws:/root/.aws \
        -e AWS_PROFILE=\"$BALCONY_AWS_PROFILE\" \
        -e AWS_DEFAULT_REGION=\"$BALCONY_AWS_DEFAULT_REGION\" \
        -e BALCONY_DEBUG=\"$BALCONY_DEBUG\" \
        -v $BALCONY_TF_GEN_OUTPUT_DIR:/balcony-output \
        --rm -it ghcr.io/oguzhan-yilmaz/balcony-terraform-import:main"
```

Brief explanation of the alias command:

- `mkdir -p $BALCONY_TF_GEN_OUTPUT_DIR`: Create the output directory if it doesn't exist
- `docker pull -q ghcr.io/oguzhan-yilmaz/balcony-terraform-import:main`: Pull the newer Docker image 
-  `echo \"Generated files will be saved to: $BALCONY_TF_GEN_OUTPUT_DIR\n\"`: inform about output directory
- `docker run`: runs the docker image with the options talked above. This kind of alias command is called a [function-like alias](https://unix.stackexchange.com/a/330002), allows us to pass arguments to our `entrypoint.sh`.


```bash title="Running the 'balcony-tf-import' alias"

balcony-tf-import ec2 Instances


balcony-tf-import iam Users
```


!!! Warning
    You can't use `--output, -o` or **any other option** with the docker image. 

    Docker image only accepts 2 arguments: `service` and `resource-name`.

