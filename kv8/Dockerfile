FROM alpine:3.9.2 AS builder

WORKDIR /app

RUN apk add --no-cache gcc cmake build-base

ADD . .

RUN cmake . && cmake --build .

FROM alpine:3.9.2

WORKDIR /app

RUN apk add --no-cache socat

COPY --from=builder /app/kv8 .

EXPOSE 4242

CMD ["socat", "-T", "5", "tcp-l:4242,fork,reuseaddr", "system:'./kv8'"]