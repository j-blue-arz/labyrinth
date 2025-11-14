FROM node:18 AS base

WORKDIR /usr/src/web-client

# copy everything but .dockerignore
COPY package.json package-lock.json ./

RUN npm ci

COPY . ./

FROM base AS test

RUN npm run test

FROM base AS lint

RUN npm run lint

FROM base AS build

RUN npm run build

FROM nginx:1.25.3 AS release

RUN rm /etc/nginx/conf.d/default.conf

COPY docker/nginx-docker.conf /etc/nginx/conf.d/
COPY --from=build /usr/src/web-client/dist /usr/share/nginx/static
