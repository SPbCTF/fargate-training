FROM i386/debian:buster

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

ADD . .

RUN apt update && \
    apt install -yq cmake gcc g++ libevent-dev gdb

RUN cmake . && cmake --build . && chmod +x start.sh

CMD ["bash", "-c", "./start.sh"]
