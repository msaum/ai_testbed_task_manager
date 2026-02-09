#!/bin/sh
# Frontend entrypoint script for environment variable substitution

set -e

echo "Starting Local Task Manager frontend..."

# Substitute API_URL environment variable in nginx config if set
if [ -n "$API_URL" ]; then
    echo "Setting API_URL to: $API_URL"
    sed -i "s|\${API_URL}|$API_URL|g" /etc/nginx/conf.d/default.conf
fi

# Run the main command
exec "$@"
