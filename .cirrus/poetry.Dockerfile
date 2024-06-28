ARG CIRRUS_AWS_ACCOUNT=275878209202
FROM ${CIRRUS_AWS_ACCOUNT}.dkr.ecr.eu-central-1.amazonaws.com/base:j17-latest

USER root

ARG PYTHON_VERSION=3.12.1

# install required dependencies to build Python from source see: https://devguide.python.org/getting-started/setup-building/#install-dependencies
RUN apt-get update && apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev
RUN curl -O https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz
RUN tar -xf Python-${PYTHON_VERSION}.tar.xz
RUN cd Python-${PYTHON_VERSION} && ./configure && make -s -j 4 && make altinstall
RUN cd /usr/local/bin \
    && ln -s python${PYTHON_VERSION%.*} python \
    && ln -s python${PYTHON_VERSION%.*} python3 \
    && ln -s pip${PYTHON_VERSION%.*} pip \
    && ln -s pip${PYTHON_VERSION%.*} pip3

USER sonarsource

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:/home/sonarsource/.local/bin"

ENV SONARCLOUD_ANALYSIS true
