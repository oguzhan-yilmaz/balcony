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
    && curl -q $(curl -sL https://releases.hashicorp.com/terraform/index.json | jq -r '.versions[].builds[].url' | sort -t. -k 1,1n -k 2,2n -k 3,3n -k 4,4n | egrep -v 'rc|beta' | egrep 'linux.*amd64' |tail -1) -o terraform.zip \
    && unzip -q terraform.zip \
    && mv terraform /usr/local/bin/ \
    && rm -rf terraform.zip \
    && pip3 install --no-cache-dir balcony \
    && terraform init -upgrade \
    && mkdir -p /balcony-output \
    && chmod +x entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh"]
