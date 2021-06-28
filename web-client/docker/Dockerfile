FROM nginx:1.19.10

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx-docker.conf /etc/nginx/conf.d/
COPY ../dist /usr/share/nginx/static
