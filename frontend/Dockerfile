FROM node:10.16.0

WORKDIR /app

COPY package*.json ./
RUN yarn install

COPY . /app
EXPOSE 3000
CMD [ "yarn", "dev" ]