#!/bin/sh
set -e  # Exit immediately if a command exits with a non-zero status

if [ "$ENV" = "production" ]; then
    # Start Nginx in the background
    echo "Starting Nginx..."
    nginx &
    
    # Wait for Nginx to start
    sleep 5

    # Check if Nginx is running
    if ! pgrep -x "nginx" > /dev/null; then
        echo "Nginx failed to start"
        exit 1
    fi

    # Obtain SSL certificates using Certbot
    echo "Obtaining SSL certificates..."
    certbot --nginx -d dp.sales.sinoplis.gr --non-interactive --agree-tos --email me@sinoplis.gr || {
        echo "Certbot failed to obtain SSL certificates"
        exit 1
    }

    # Start Flask application with Gunicorn
    echo "Starting Flask application with Gunicorn..."
    gunicorn --bind 0.0.0.0:5000 app:app &

    # Wait for Gunicorn to start
    sleep 5

    # Check if Gunicorn is running
    if ! pgrep -x "gunicorn" > /dev/null; then
        echo "Gunicorn failed to start"
        exit 1
    fi

    # Setup a cron job for certificate renewal
    echo "Setting up cron job for certificate renewal..."
    echo "0 0 * * * certbot renew --quiet --post-hook 'nginx -s reload'" | crontab -

    # Start the cron daemon in the foreground
    echo "Starting cron daemon..."
    cron -f
else
    # Development mode: Start Flask application without Nginx and certificates
    echo "Starting Flask application in development mode..."
    export FLASK_APP=run:app
    flask run --host=0.0.0.0 --port=5000
fi
