FROM node:alpine AS builder

WORKDIR /app

COPY . .

RUN yarn install && yarn dist

FROM node:alpine

WORKDIR /app

COPY --from=builder /app/dist  /app/package.json /app/yarn.lock ./

RUN yarn install --production

CMD ["yarn", "start:docker"]