FROM python:3.11-slim-bullseye


ENV GEN_TF_DIR /terraform-app

WORKDIR $GEN_TF_DIR

# prepared provider.tf with the aws provider block for build-time 'terraform init'
COPY dockerfiles/provider.tf $GEN_TF_DIR/provider.tf

# copy over the entrypoint script
COPY --chmod=0755 dockerfiles/entrypoint.sh entrypoint.sh

RUN apt update -y \
    && apt install -y curl unzip bat \ 
    && apt autoremove -y \
    && curl -q https://releases.hashicorp.com/terraform/1.5.1/terraform_1.5.1_linux_amd64.zip -o terraform.zip \
    && unzip -q terraform.zip \
    && mv terraform /usr/local/bin/ \
    && rm -rf terraform.zip \
    && pip3 install --no-cache-dir balcony \
    && echo "trigger a whole new build" \
    && terraform init -upgrade \
    && chmod +x entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh"]
