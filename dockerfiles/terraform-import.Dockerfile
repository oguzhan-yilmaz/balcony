FROM python:3.11-slim-bullseye


ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.5.1

# System deps:
RUN pip install "poetry==$POETRY_VERSION"


ENV GEN_TF_DIR /terraform-app

# Copy only requirements to cache them in docker layer
WORKDIR /code


COPY poetry.lock pyproject.toml /code/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Creating folders, and files for a project:

RUN apt update -y \
    && apt install -y curl unzip -y \ 
    && apt autoremove -y 



# RUN pip3 install --no-cache-dir balcony

# TODO: extract out the used version of terraform
RUN  curl https://releases.hashicorp.com/terraform/1.5.1/terraform_1.5.1_linux_amd64.zip -o terraform.zip \
    && unzip -q terraform.zip \
    && mv terraform /usr/local/bin/ \
    && rm -rf terraform.zip 

WORKDIR $GEN_TF_DIR

# prepared provider.tf with the aws provider block for build-time 
# 'terraform init'-ialization
COPY dockerfiles/provider.tf $GEN_TF_DIR/provider.tf
RUN  echo "running terraform init"; terraform init -upgrade

WORKDIR /code

COPY . /code

COPY dockerfiles/entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh
ENTRYPOINT [ "./entrypoint.sh"]


# CMD [ "sleep", "50000"]
# ENTRYPOINT [ "balcony" ]