#!/bin/sh
set -e

# Generate app key if not set
php artisan key:generate --force --no-interaction 2>/dev/null || true

# Run database migrations + seed (idempotent: updateOrCreate in seeder)
php artisan migrate --force --no-interaction
php artisan db:seed --force --no-interaction

# Optimise for production
php artisan config:cache
php artisan route:cache
php artisan view:cache

exec "$@"
