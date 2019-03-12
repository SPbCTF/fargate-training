FROM alpine AS builder

WORKDIR /app

ADD . .

RUN apk add --no-cache gcc cmake build-base

RUN cmake . && cmake --build .

FROM alpine

WORKDIR /app

RUN apk add --no-cache socat

COPY --from=builder /app/kv8 .

EXPOSE 4242

CMD ["socat", "-T", "5", "tcp-l:4242,fork,reuseaddr", "system:'./kv8'"]