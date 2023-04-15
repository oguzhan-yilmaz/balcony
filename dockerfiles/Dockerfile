FROM python:3.11

RUN apt update -y && apt install -y curl unzip groff

# install aws-cli and 
# pip install balcony
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip -q awscliv2.zip \
    && ./aws/install \
    && pip3 install --no-cache-dir balcony

    
ENTRYPOINT [ "balcony" ]