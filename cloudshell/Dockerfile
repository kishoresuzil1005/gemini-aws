FROM amazonlinux:2023

RUN dnf update -y && \
    dnf install -y \
    awscli \
    python3 \
    unzip \
    curl && \
    dnf clean all

RUN curl -LO https://releases.hashicorp.com/terraform/1.9.0/terraform_1.9.0_linux_amd64.zip && \
    unzip terraform_1.9.0_linux_amd64.zip && \
    mv terraform /usr/local/bin/

CMD ["sleep","infinity"]
