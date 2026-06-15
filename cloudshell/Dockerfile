FROM amazonlinux:2023

RUN yum install -y \
    python3 \
    unzip \
    curl \
    python3-pip

RUN pip3 install \
    fastapi \
    uvicorn \
    boto3

RUN curl -LO \
https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip

RUN unzip awscli-exe-linux-x86_64.zip

RUN ./aws/install

WORKDIR /app

COPY main.py .

EXPOSE 9000

CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000" ]
