FROM amazonlinux:2023

RUN dnf update -y && \
    dnf install -y \
    awscli \
    python3 \
    python3-pip \
    unzip && \
    dnf clean all

WORKDIR /app

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

RUN curl -LO https://releases.hashicorp.com/terraform/1.9.0/terraform_1.9.0_linux_amd64.zip && \
    unzip terraform_1.9.0_linux_amd64.zip && \
    mv terraform /usr/local/bin/

EXPOSE 9000

CMD [ \
    "uvicorn", \
    "main:app", \
    "--host", \
    "0.0.0.0", \
    "--port", \
    "9000" \
]
