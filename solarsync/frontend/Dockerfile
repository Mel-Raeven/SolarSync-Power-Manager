# syntax=docker/dockerfile:1

# ----------------------------------------------------------------
# Stage 1: Node — build frontend assets (runs on native amd64,
#           output is architecture-independent JS/CSS)
# ----------------------------------------------------------------
FROM --platform=linux/amd64 node:20-alpine AS node-builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# ----------------------------------------------------------------
# Stage 2: PHP-FPM runtime (arm64)
# ----------------------------------------------------------------
FROM php:8.4-fpm

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    libzip-dev \
    libsqlite3-dev \
    zip \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install PHP extensions required by Laravel
RUN docker-php-ext-install \
    pdo \
    pdo_sqlite \
    mbstring \
    exif \
    pcntl \
    bcmath \
    gd \
    zip \
    xml

# Install Composer
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

WORKDIR /var/www

COPY . .

# Copy compiled assets from the Node stage
COPY --from=node-builder /app/public/build ./public/build

# Install PHP dependencies (prod only, autoloader optimised)
RUN composer install --no-dev --optimize-autoloader --no-interaction

# Set permissions for Laravel storage and bootstrap cache
RUN chown -R www-data:www-data /var/www/storage /var/www/bootstrap/cache \
    && chmod -R 775 /var/www/storage /var/www/bootstrap/cache

# Shared data volume mount point (SQLite lives here)
RUN mkdir -p /data && chown www-data:www-data /data

# Entrypoint: generate app key if missing, run migrations + seed, start PHP-FPM
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 9000

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["php-fpm"]
