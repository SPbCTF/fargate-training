FROM python:3-alpine

WORKDIR /cryptostorm

RUN apk add --no-cache dumb-init gcc build-base

ADD requirements.txt .

RUN pip install -r requirements.txt

ADD . .

RUN apk del gcc build-base

EXPOSE 22228

ENV FLASK_APP=__init__.py

ENTRYPOINT ["dumb-init", "--"]
CMD ["flask", "run", "-h", "0.0.0.0", "-p", "22228", "--with-threads"]