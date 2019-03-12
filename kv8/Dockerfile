FROM debian:buster-20190228-slim AS builder

WORKDIR /app

RUN apt-get update
RUN apt-get install -y gcc cmake

ADD . .

RUN cmake . && cmake --build .

FROM debian:buster-20190228-slim

WORKDIR /app

RUN apt-get update
RUN apt-get install -y socat

COPY --from=builder /app/kv8 .

EXPOSE 4242

CMD ["socat", "-T", "5", "tcp-l:4242,fork,reuseaddr", "system:'./kv8'"]