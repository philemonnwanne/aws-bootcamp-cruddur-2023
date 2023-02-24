# build image
FROM node:16.17.0-bullseye-slim AS build

WORKDIR /frontend-react-js

COPY --chown=node:node package.json /frontend-react-js/

ENV NODE_ENV=production

RUN npm install --production

# production image
FROM node:lts-alpine3.17

ENV NODE_ENV production

WORKDIR /frontend-react-js

USER node

COPY --from=build /frontend-react-js/node_modules /frontend-react-js/node_modules

COPY --chown=node:node . /frontend-react-js/

CMD ["npm", "start"]
