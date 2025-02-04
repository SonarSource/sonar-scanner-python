ARG CIRRUS_AWS_ACCOUNT=275878209202
FROM ${CIRRUS_AWS_ACCOUNT}.dkr.ecr.eu-central-1.amazonaws.com/base:j17-latest
USER root
ARG PYTHON_VERSION=3.12.1
ENV POETRY_VERSION 2.0.1

RUN apt-get update && \
    apt-get install -y pipx  \
    && rm -rf /var/lib/apt/lists/*
USER sonarsource
RUN pipx install uv
ENV PATH=${PATH}:/home/sonarsource/.local/bin
WORKDIR /home/sonarsource
RUN uv python install ${PYTHON_VERSION} --default --preview && \
    uv tool install poetry==${POETRY_VERSION}