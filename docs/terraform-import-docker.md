# balcony terraform-import on Docker


`balcony terraform-import` command allows us to get the import blocks for the resources in our AWS account.

But it's still not generating the actual Terraform code for us. Let's fix that.

## Docker Image

- Github Container Registry: [balcony-terraform-import](https://github.com/oguzhan-yilmaz/balcony/pkgs/container/balcony-terraform-import)

- Dockerfile: [terraform-import.Dockerfile](https://github.com/oguzhan-yilmaz/balcony/blob/main/dockerfiles/terraform-import.Dockerfile)

```bash title="Pull the balcony-terraform-import image"
docker pull ghcr.io/oguzhan-yilmaz/balcony-terraform-import:main
```

This Docker image installs `balcony` and `terraform v.1.5+` on top of the `python:3.9-slim-buster` image.

It also copies over the `entrypoint.sh` and `provider.tf` files to image.










## Alias Commands


```bash title="Alias with ~.aws/ folder mounted"


alias balcony-tf-import='docker run \
  -v ~/.aws:/root/.aws \
  -v ~/tf_gen_outputs:/terraform_app \
  -e AWS_PROFILE="default" \
  -e AWS_DEFAULT_REGION="eu-west-1" \
  --rm -it ghcr.io/oguzhan-yilmaz/balcony-terraform-import:main'
```




```bash title="Alias with ~.aws/ folder mounted"




alias balcony-tf-import='mkdir -p /tmp/balcony-terraform-gen \
    && docker pull ghcr.io/oguzhan-yilmaz/balcony-terraform-import:main \
    && docker run \
        -v ~/.aws:/root/.aws \
        -v /tmp/balcony-terraform-gen:/terraform_app \
        -e AWS_PROFILE="hepapi" \
        -e AWS_DEFAULT_REGION="eu-west-1" \
        --rm -it ghcr.io/oguzhan-yilmaz/balcony-terraform-import:main \
    && echo "Generated files are saved to: /tmp/balcony-terraform-gen"'






```



