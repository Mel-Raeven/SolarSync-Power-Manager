#!/usr/bin/env bash
# generate-certs.sh
# Generates a self-signed TLS certificate for local HTTPS on the Pi.
# Run once on first setup. For production use, replace with Let's Encrypt.

set -euo pipefail

CERT_DIR="$(dirname "${BASH_SOURCE[0]}")/../nginx/certs"
CERT_DIR="$(realpath -m "$CERT_DIR")"
CERT_FILE="$CERT_DIR/solarsync.crt"
KEY_FILE="$CERT_DIR/solarsync.key"

if [[ -f "$CERT_FILE" && -f "$KEY_FILE" ]]; then
    echo "Certificates already exist at $CERT_DIR — skipping generation."
    echo "Delete $CERT_FILE and $KEY_FILE to regenerate."
    exit 0
fi

mkdir -p "$CERT_DIR"

echo "Generating self-signed certificate in $CERT_DIR ..."

openssl req -x509 \
    -nodes \
    -days 3650 \
    -newkey rsa:2048 \
    -keyout "$KEY_FILE" \
    -out "$CERT_FILE" \
    -subj "/C=NL/ST=Local/L=Home/O=SolarSync/CN=solarsync.local" \
    -addext "subjectAltName=DNS:solarsync.local,DNS:localhost,IP:127.0.0.1"

chmod 600 "$KEY_FILE"
chmod 644 "$CERT_FILE"

echo ""
echo "Done. Certificate details:"
openssl x509 -noout -subject -dates -in "$CERT_FILE"
echo ""
echo "To trust this certificate on your devices, copy $CERT_FILE"
echo "to each device and add it as a trusted CA."
