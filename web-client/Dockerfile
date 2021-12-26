FROM node:14 as base

WORKDIR /usr/src/web-client

# copy everything but .dockerignore
COPY . ./

RUN npm ci

FROM base as test

RUN npm run lint
RUN npm run test:unit

FROM base as build

RUN npm run build

FROM nginx:1.19.10 as release

RUN rm /etc/nginx/conf.d/default.conf

COPY docker/nginx-docker.conf /etc/nginx/conf.d/
COPY --from=build /usr/src/web-client/dist /usr/share/nginx/static
