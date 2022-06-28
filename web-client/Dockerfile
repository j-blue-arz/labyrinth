FROM node:16 as base

WORKDIR /usr/src/web-client

# copy everything but .dockerignore
COPY package.json package-lock.json ./

RUN npm ci

COPY . ./

FROM base as test

RUN npm run test:unit

FROM base as lint

RUN npm run lint

FROM base as build

RUN npm run build

FROM nginx:1.19.10 as release

RUN rm /etc/nginx/conf.d/default.conf

COPY docker/nginx-docker.conf /etc/nginx/conf.d/
COPY --from=build /usr/src/web-client/dist /usr/share/nginx/static
