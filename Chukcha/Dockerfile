FROM debian:buster-slim AS builder

ENV DEBIAN_FRONTEND=noninteractive

RUN dpkg --add-architecture i386 && \
    apt update && \
    apt install -y cmake gcc-multilib g++-multilib libevent-dev:i386 socat

WORKDIR /app

ADD . .

RUN cmake . && cmake --build . && chmod +x start.sh

CMD ["bash", "-c", "./start.sh"]
