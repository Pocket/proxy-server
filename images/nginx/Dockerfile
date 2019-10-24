FROM nginx:1.17

RUN apt-get update && \
    apt-get install -y curl

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/nginx.conf
