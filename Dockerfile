ARG ARCH=
FROM ${ARCH}debian:bullseye

RUN apt-get update && \
    apt-get upgrade -y && \
    DEBIAN_FRONTEND=noninteractive apt-get -yq install \
    git \
    python3 \
    python3-pip \
    tzdata

ENV TZ=Europe/Berlin

RUN mkdir -p /app/data/

WORKDIR /app

COPY . /app

RUN python3 -m pip install -e .

CMD discord-bot
