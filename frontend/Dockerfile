FROM node:16-alpine

WORKDIR /app

COPY package.json package-lock.json /app/

RUN npm install && npm install react-scripts

COPY . /app/

EXPOSE 3000

CMD ["npm", "start"]
