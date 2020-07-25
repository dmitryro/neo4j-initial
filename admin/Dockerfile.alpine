FROM mhart/alpine-node:latest
WORKDIR /dist
COPY package*.json ./

COPY . /dist

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN \
  apk update                     && \
  apk add bash                   && \
  apk add --no-cache python3 python3-dev && \ 
  npm install -G yarn typescript && \
  npx -p @ant-design/codemod-v4 antd4-codemod ./src --force && \
  yarn global add @ant-design/codemod-v4 && \
  antd4-codemod ./src --force && \ 
  yarn

EXPOSE 8080
