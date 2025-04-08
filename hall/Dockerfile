FROM node:20-alpine

ADD . /app
WORKDIR /app

RUN rm -rf node_modules && npm install

CMD ["npm", "run", "dev"]