FROM python:3-alpine

WORKDIR /app

ADD requirements.txt .

RUN pip install -r requirements.txt && apk add --no-cache dumb-init

ADD . .

EXPOSE 5000

ENTRYPOINT ["dumb-init", "--"]
CMD ["python", "haveibeenpwned.py"]