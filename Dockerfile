FROM python:3-alpine

ENV KUBECTL_VERSION=1.16.2
ENV HELM_VERSION=2.16.1
ENV RANCHER_CLI_VERSION=2.3.2

RUN apk update && apk add --no-cache git curl ca-certificates tar

RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/v$KUBECTL_VERSION/bin/linux/amd64/kubectl && \
    chmod +x kubectl && \
    mv kubectl /bin/kubectl

RUN curl -LO https://get.helm.sh/helm-v$HELM_VERSION-linux-amd64.tar.gz && \
    tar -zxf helm-v$HELM_VERSION-linux-amd64.tar.gz --no-same-owner && \
    rm helm-v$HELM_VERSION-linux-amd64.tar.gz && \
    chmod +x linux-amd64/helm && \
    mv linux-amd64/helm /bin/helm && \
    rm -r linux-amd64

RUN curl -LO https://github.com/rancher/cli/releases/download/v$RANCHER_CLI_VERSION/rancher-linux-amd64-v$RANCHER_CLI_VERSION.tar.gz && \
    tar -zxf rancher-linux-amd64-v$RANCHER_CLI_VERSION.tar.gz --no-same-owner && \
    rm rancher-linux-amd64-v$RANCHER_CLI_VERSION.tar.gz && \
    chmod +x rancher-v$RANCHER_CLI_VERSION/rancher && \
    mv rancher-v$RANCHER_CLI_VERSION/rancher /bin/rancher && \
    rm -r rancher-v$RANCHER_CLI_VERSION

RUN mkdir /root/.kube && \
    touch /root/.kube/config && \
    mkdir /source

WORKDIR /usr/src/app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir storage

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "--worker-class", "gthread", "--log-level", "error", "app:app"]
