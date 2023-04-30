# balcony on Docker

Visit the Github packages for balcony: [ghcr.io/oguzhan-yilmaz/balcony](https://github.com/oguzhan-yilmaz/balcony/pkgs/container/balcony)

## Pulling balcony from GitHub Container Registry

```bash
docker pull ghcr.io/oguzhan-yilmaz/balcony:latest
```

## Alias for running balcony with Docker

```bash
alias balcony='docker run --rm -ti \
                -v ~/.aws:/root/.aws \
                -e AWS_PROFILE="default" \
                -e AWS_DEFAULT_REGION="eu-west-1" \
                ghcr.io/oguzhan-yilmaz/balcony:latest'
```

This alias command will mount your `~/.aws` directory to the created container for the AWS access. With this configuration, your `default` AWS Profile would be used in the `eu-west-1` region.


After running the command, you can use balcony as usual.

```bash
balcony info

balcony aws ec2 Instance --list

balcony aws s3 Policy --paginate --debug
```

You can copy the alias command to your `.bashrc` or `.zshrc` to persist it.

!!! note "`--screen`, `-s` option will not be usable"

    As you run the balcony commands on docker, you don't get an interactive terminal, so the `--screen`, `-s` option will be useless.

## Running balcony w/ AWS Credential Env. Variables

You may configure your AWS Credentials by adding required environment variables on docker run, instead of mounting your `~/.aws` directory.

```bash
alias balcony='docker run --rm -ti  \
    -e AWS_DEFAULT_REGION="eu-west-1" \
    -e AWS_ACCESS_KEY_ID="..." \
    -e AWS_SECRET_ACCESS_KEY="..." \
    ghcr.io/oguzhan-yilmaz/balcony:latest'
```

```bash
balcony aws ec2 Instances
```

## Building balcony Docker Image locally
```bash
# build the image and tag it
docker build -t balcony-local .
```

```bash
# alias balcony docker image to a single command
alias balcony='docker run --rm -ti \
                -v ~/.aws:/root/.aws \
                -e AWS_PROFILE="default" \
                -e AWS_DEFAULT_REGION="eu-west-1" \
                balcony-local'
```


```bash
balcony info

balcony aws ec2 Instances --debug
```
