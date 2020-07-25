FROM python:3.8.4-alpine

ENV C_FORCE_ROOT true

ENV HOST 0.0.0.0
ENV PORT 5000
ENV DEBUG true

COPY ./entrypoint.sh /entrypoint.sh
COPY . /api
WORKDIR /api
RUN chmod +x /entrypoint.sh
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add --no-cache postgresql-dev gcc python3-dev musl-dev openssl-dev libffi-dev build-base
RUN pip install --upgrade pip
# install requirements
RUN pip install -r requirements.txt
# expose the app port
EXPOSE 5000
# run the app server
#ENTRYPOINT ["/entrypoint.sh"]

# run the app server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "5", "app:app", "--log-level", "debug", "--timeout", "120"]
