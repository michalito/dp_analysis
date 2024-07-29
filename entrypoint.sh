#!/bin/sh

if [ "$ENV" = "production" ]; then
    # Start Nginx in the background
    nginx &

    # Wait for Nginx to start
    sleep 5

    # Obtain SSL certificates using Certbot
    certbot --nginx -d dp.sales.sinoplis.gr --non-interactive --agree-tos --email me@sinoplis.gr

    # Start Flask application
    python app.py &

    # Setup a cron job for certificate renewal
    echo "0 0 * * * certbot renew --quiet --post-hook 'nginx -s reload'" | crontab -

    # Start the cron daemon in the foreground
    cron -f
else
    # Development mode: Start Flask application without Nginx and certificates
    python app.py
fi
