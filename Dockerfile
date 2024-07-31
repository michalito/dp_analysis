FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y \
    nginx \
    certbot \
    python3-certbot-nginx \
    cron \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --system nginx \
    && adduser --system --no-create-home --disabled-login --disabled-password --group nginx

# Use build argument
ARG ADMIN_PASSWORD
ENV ADMIN_PASSWORD=${ADMIN_PASSWORD}
ARG FLASK_SECRET_KEY
ENV FLASK_SECRET_KEY=${FLASK_SECRET_KEY}

COPY nginx.conf /etc/nginx/nginx.conf
COPY default.conf /etc/nginx/conf.d/default.conf

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80
EXPOSE 443

CMD ["/entrypoint.sh"]
