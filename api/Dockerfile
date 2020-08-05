FROM python:3.8.5-alpine
ENV C_FORCE_ROOT true

ENV PIP_FORMAT=legacy
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV KAFKA_BOOSTRAP_SERVER_PORT 9092
ENV KAFKA_BOOSTRAP_SERVER_NAME kafka:9092
ENV KAFKA_BROKER kafka://kafka:9092
ENV KAFKA_BOOTSTRAP_SERVER kafka:9092
ENV SCHEMA_REGISTRY_SERVER_PORT 8081
ENV SCHEMA_REGISTRY_SERVER schema-registry:8081
ENV NEO4J_SERVER neo4j
ENV NEO4J_SERVER_PORT=7687
ENV HOST 0.0.0.0
ENV PORT 5000
ENV DEBUG true

COPY . /api
WORKDIR /api

COPY . .
RUN chmod +x ./wait_for_services.sh
RUN chmod +x ./run.sh

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add --no-cache bash postgresql-dev libxml2-dev libxslt-dev gcc python3-dev linux-headers musl-dev openssl-dev libffi-dev build-base

RUN pip install --upgrade pip
# install requirements
RUN pip install -r requirements.txt
# expose the app port
EXPOSE 5000
# run the app server
#ENTRYPOINT ["/entrypoint.sh"]

# run the app server
#CMD ["flask", "run", "--port", "5000"]
ENTRYPOINT ["./wait_for_services.sh"]
CMD ["./run.sh", "${WORKER}", "${WORKER_PORT}", "${CONFIG_CLASS}"]
