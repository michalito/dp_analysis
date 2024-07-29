# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Nginx, Certbot, and cron for production and create nginx user and group
RUN apt-get update && apt-get install -y \
    nginx \
    certbot \
    python3-certbot-nginx \
    cron \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --system nginx \
    && adduser --system --no-create-home --disabled-login --disabled-password --group nginx

# Make environment variable for admin password
ARG ADMIN_PASSWORD
ENV ADMIN_PASSWORD=${ADMIN_PASSWORD}

# Copy Nginx configuration files
COPY nginx.conf /etc/nginx/nginx.conf
COPY default.conf /etc/nginx/conf.d/default.conf

# Copy the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Make ports 80 and 443 available to the world outside this container
EXPOSE 80
EXPOSE 443

# Run the entrypoint script when the container launches
CMD ["/entrypoint.sh"]
