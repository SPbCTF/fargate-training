FROM debian:buster-20190228-slim
WORKDIR /app
RUN apt-get update
RUN apt-get install -y socat
ADD kv8 /app/kv8
EXPOSE 4242
CMD ["socat", "-T", "5", "tcp-l:4242,fork,reuseaddr", "system:'/app/kv8'"]