FROM node:10.16.0

WORKDIR /app

COPY package*.json ./
# RUN yarn build

COPY . /app
EXPOSE 3000
CMD [ "yarn", "dev" ]