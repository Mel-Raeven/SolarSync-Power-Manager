#!/bin/sh
set -e

# Generate app key only if not already set (install.sh pre-generates it;
# this is a fallback for manual setups that skip the installer)
if [ -z "${APP_KEY}" ] || [ "${APP_KEY}" = "base64:CHANGE_ME" ]; then
  php artisan key:generate --force --no-interaction
fi

# Run database migrations + seed (idempotent: updateOrCreate in seeder)
php artisan migrate --force --no-interaction
php artisan db:seed --force --no-interaction

# Optimise for production
php artisan config:cache
php artisan route:cache
php artisan view:cache

exec "$@"
