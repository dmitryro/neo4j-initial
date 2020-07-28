FROM mhart/alpine-node:12
#FROM circleci/node:latest-browsers

WORKDIR /dist
USER root
COPY package.json ./
COPY . /dist
RUN chmod +x /dist

#npm run test:all

#RUN npm run fetch:blocks
RUN yarn
EXPOSE 8082

CMD ["yarn", "start"]
