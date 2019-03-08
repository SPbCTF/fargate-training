FROM node:alpine

WORKDIR /app

ADD . .

RUN yarn install

RUN yarn build

CMD ["yarn", "start"]