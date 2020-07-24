# start from an official image
FROM python:3.9.0b3-alpine
# arbitrary location choice: you can change the directory
# install psycopg2 dependencies
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apk update \
    && apk add --no-cache git bash gcc python3-dev jpeg-dev zlib-dev musl-dev openssl-dev libffi-dev build-base
RUN pip install --upgrade pip
RUN mkdir -p /opt/services/slackbot
WORKDIR /opt/services/slackbot

# install our dependencies
# we use --system flag because we don't need an extra virtualenv
COPY . .
COPY . /opt/services/slackbot
RUN pip install -r requirements.txt \
    && python setup.py install
