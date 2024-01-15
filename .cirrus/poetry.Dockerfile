ARG CIRRUS_AWS_ACCOUNT=275878209202
FROM ${CIRRUS_AWS_ACCOUNT}.dkr.ecr.eu-central-1.amazonaws.com/base:j17-latest

USER root

ARG SCANNER_VERSION=5.0.1.3006
ARG PYTHON_VERSION=3.12.1

RUN apt-get update && apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev grep
RUN apt-get install -y dbus-user-session uidmap
RUN curl -O https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz
RUN tar -xf Python-${PYTHON_VERSION}.tar.xz
RUN cd Python-${PYTHON_VERSION} && ./configure --enable-optimizations && make -j 4 && make altinstall
RUN cd /usr/local/bin \
    && ln -s python${PYTHON_VERSION%.*} python \
    && ln -s python${PYTHON_VERSION%.*} python3 \
    && ln -s pip${PYTHON_VERSION%.*} pip \
    && ln -s pip${PYTHON_VERSION%.*} pip3

RUN curl "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-${SCANNER_VERSION}.zip" -o /tmp/sonar-scanner.zip \
  && unzip -d /opt /tmp/sonar-scanner.zip \
  && mv /opt/sonar-scanner-${SCANNER_VERSION} /opt/sonar-scanner \
  && rm /tmp/sonar-scanner.zip

USER sonarsource

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH=/usr/bin:$PATH
ENV PATH="/home/sonarsource/bin:${PATH}"
ENV PATH="${PATH}:/opt/sonar-scanner/bin"
ENV PATH="${PATH}:/home/sonarsource/.local/bin"

ENV SONARCLOUD_ANALYSIS true

