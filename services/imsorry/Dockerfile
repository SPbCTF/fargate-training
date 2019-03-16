FROM ruby:alpine

# throw errors if Gemfile has been modified since Gemfile.lock
RUN bundle config --global frozen 1

WORKDIR /usr/src/app

COPY Gemfile Gemfile.lock ./

RUN apk add --no-cache gcc build-base sqlite-dev

RUN bundle install

RUN apk del gcc build-base

COPY . .

CMD ["rackup", "-o", "0.0.0.0", "-p",  "14567"]
