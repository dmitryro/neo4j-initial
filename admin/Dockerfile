FROM circleci/node:latest-browsers

WORKDIR /usr/src/app/
USER root
COPY package.json ./
RUN yarn

COPY ./ ./

#npm run test:all

#RUN npm run fetch:blocks

EXPOSE 8000

CMD ["yarn", "start"]
