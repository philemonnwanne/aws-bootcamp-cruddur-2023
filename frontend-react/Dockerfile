# build/development image
FROM node:16.17.0-bullseye-slim AS build

WORKDIR /frontend-react

COPY --chown=node:node ./*.json .

ENV NODE_ENV=development

RUN npm install
        # @opentelemetry/api \
        # @opentelemetry/sdk-trace-web \
        # @opentelemetry/exporter-trace-otlp-http \
        # @opentelemetry/context-zone \
        # @opentelemetry/instrumentation \
        # aws-amplify

# production image
FROM node:lts-alpine3.17

ENV NODE_ENV production

WORKDIR /frontend-react

USER node

COPY --from=build /frontend-react/node_modules /frontend-react/node_modules

COPY --chown=node:node . .

CMD ["npm", "start"]
