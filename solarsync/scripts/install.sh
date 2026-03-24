#!/usr/bin/env bash
# ==============================================================================
# SolarSync Power Manager — First-time installer for Raspberry Pi
# ==============================================================================
# Run as the pi user (not root). The script will use sudo where needed.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/Mel-Raeven/SolarSync-Power-Manager/main/solarsync/scripts/install.sh | bash
#
# Or, if you already cloned the repo:
#   bash solarsync/scripts/install.sh
# ==============================================================================

set -euo pipefail

REPO_URL="https://github.com/Mel-Raeven/SolarSync-Power-Manager.git"
INSTALL_DIR="${HOME}/solarsync"
SOLARSYNC_DIR="${INSTALL_DIR}/solarsync"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'  # No colour

info()    { echo -e "${CYAN}[solarsync]${NC} $*"; }
success() { echo -e "${GREEN}[solarsync]${NC} $*"; }
warn()    { echo -e "${YELLOW}[solarsync]${NC} $*"; }
error()   { echo -e "${RED}[solarsync] ERROR:${NC} $*" >&2; exit 1; }

# --------------------------------------------------------------------------
# 1. Check OS / architecture
# --------------------------------------------------------------------------
info "Checking system..."
ARCH=$(uname -m)
if [[ "${ARCH}" != "aarch64" && "${ARCH}" != "x86_64" ]]; then
  warn "Unexpected architecture: ${ARCH}. Continuing anyway, but arm64 is the tested target."
fi

OS=$(grep -E '^ID=' /etc/os-release 2>/dev/null | cut -d= -f2 | tr -d '"')
info "OS: ${OS}, arch: ${ARCH}"

# --------------------------------------------------------------------------
# 2. Set hostname to 'solarsync' and enable mDNS (avahi)
# --------------------------------------------------------------------------
CURRENT_HOSTNAME=$(hostname)
if [[ "${CURRENT_HOSTNAME}" != "solarsync" ]]; then
  info "Setting hostname to 'solarsync'..."
  echo "solarsync" | sudo tee /etc/hostname > /dev/null
  sudo sed -i "s|127\.0\.1\.1.*|127.0.1.1\tsolarsync|" /etc/hosts
  sudo hostname solarsync
  success "Hostname set to 'solarsync'."
else
  success "Hostname is already 'solarsync'."
fi

if command -v avahi-daemon &>/dev/null; then
  success "avahi-daemon already installed."
else
  info "Installing avahi-daemon for mDNS (solarsync.local)..."
  sudo apt-get update -qq
  sudo apt-get install -y avahi-daemon
  success "avahi-daemon installed."
fi

sudo systemctl enable avahi-daemon --now 2>/dev/null || true
success "SolarSync will be reachable at https://solarsync.local on your local network."

# --------------------------------------------------------------------------
# 2. Install Docker (if not present)
# --------------------------------------------------------------------------
if command -v docker &>/dev/null; then
  success "Docker already installed: $(docker --version)"
else
  info "Installing Docker..."
  curl -fsSL https://get.docker.com | sudo sh
  sudo usermod -aG docker "${USER}"
  success "Docker installed. Note: you may need to log out and back in for group membership to take effect."
fi

# Docker Compose v2 (plugin)
if docker compose version &>/dev/null; then
  success "Docker Compose already available: $(docker compose version)"
else
  info "Installing Docker Compose plugin..."
  sudo apt-get update -qq
  sudo apt-get install -y docker-compose-plugin
  success "Docker Compose installed."
fi

# --------------------------------------------------------------------------
# 3. Clone or update the repository
# --------------------------------------------------------------------------
if [[ -d "${INSTALL_DIR}/.git" ]]; then
  info "Repository already present at ${INSTALL_DIR} — pulling latest..."
  git -C "${INSTALL_DIR}" pull --ff-only
else
  info "Cloning SolarSync repository to ${INSTALL_DIR}..."
  git clone "${REPO_URL}" "${INSTALL_DIR}"
fi

# --------------------------------------------------------------------------
# 4. Create and fully populate .env (if not already present)
# --------------------------------------------------------------------------
ENV_FILE="${SOLARSYNC_DIR}/.env"
EXAMPLE_FILE="${SOLARSYNC_DIR}/.env.example"

if [[ -f "${ENV_FILE}" ]]; then
  info ".env already exists — skipping secret generation."
else
  if [[ ! -f "${EXAMPLE_FILE}" ]]; then
    error ".env.example not found at ${EXAMPLE_FILE}"
  fi
  cp "${EXAMPLE_FILE}" "${ENV_FILE}"

  # -- Auto-generate internal API key (Laravel <-> FastAPI shared secret) --
  INTERNAL_API_KEY=$(openssl rand -hex 32)
  sed -i "s|^INTERNAL_API_KEY=.*|INTERNAL_API_KEY=${INTERNAL_API_KEY}|" "${ENV_FILE}"
  success "Internal API key auto-generated."

  # -- Auto-generate Laravel APP_KEY (base64:random 32 bytes) --
  APP_KEY="base64:$(openssl rand -base64 32)"
  sed -i "s|^APP_KEY=.*|APP_KEY=${APP_KEY}|" "${ENV_FILE}"
  success "Laravel application key auto-generated."
fi

# --------------------------------------------------------------------------
# 4b. Populate frontend/.env from root .env (if not already present)
# --------------------------------------------------------------------------
FRONTEND_ENV="${SOLARSYNC_DIR}/frontend/.env"
FRONTEND_EXAMPLE="${SOLARSYNC_DIR}/frontend/.env.example"

if [[ -f "${FRONTEND_ENV}" ]]; then
  info "frontend/.env already exists — skipping."
else
  if [[ ! -f "${FRONTEND_EXAMPLE}" ]]; then
    error "frontend/.env.example not found at ${FRONTEND_EXAMPLE}"
  fi
  cp "${FRONTEND_EXAMPLE}" "${FRONTEND_ENV}"

  # Pull the generated values from the root .env and write them into frontend/.env
  _read_env() { grep -E "^${1}=" "${ENV_FILE}" | cut -d= -f2- | tr -d '"' || true; }

  APP_KEY_VAL=$(_read_env APP_KEY)
  INTERNAL_KEY_VAL=$(_read_env INTERNAL_API_KEY)

  sed -i "s|^APP_KEY=.*|APP_KEY=${APP_KEY_VAL}|" "${FRONTEND_ENV}"
  sed -i "s|^INTERNAL_API_KEY=.*|INTERNAL_API_KEY=${INTERNAL_KEY_VAL}|" "${FRONTEND_ENV}"

  success "frontend/.env populated."
fi

# --------------------------------------------------------------------------
# 5. Generate TLS certificates (if not already present)
# --------------------------------------------------------------------------
CERT_DIR="${SOLARSYNC_DIR}/nginx/certs"
if [[ -f "${CERT_DIR}/solarsync.crt" && -f "${CERT_DIR}/solarsync.key" ]]; then
  info "TLS certificates already present — skipping."
else
  info "Generating self-signed TLS certificate..."
  bash "${SOLARSYNC_DIR}/scripts/generate-certs.sh"
  success "TLS certificate generated at ${CERT_DIR}/"
fi

# --------------------------------------------------------------------------
# 5b. Generate Mosquitto password file (if not already present)
# --------------------------------------------------------------------------
MQTT_PASSWD_FILE="${SOLARSYNC_DIR}/mosquitto/passwd"

if [[ -f "${MQTT_PASSWD_FILE}" ]]; then
  info "Mosquitto password file already present — skipping."
else
  # Auto-generate random MQTT credentials — internal between Docker services only.
  MQTT_USERNAME="solarsync"
  MQTT_PASSWORD=$(openssl rand -hex 24)

  sed -i "s|^MQTT_USERNAME=.*|MQTT_USERNAME=${MQTT_USERNAME}|" "${ENV_FILE}"
  sed -i "s|^MQTT_PASSWORD=.*|MQTT_PASSWORD=${MQTT_PASSWORD}|" "${ENV_FILE}"

  info "Generating Mosquitto password file..."
  mkdir -p "${SOLARSYNC_DIR}/mosquitto"
  if command -v mosquitto_passwd &>/dev/null; then
    mosquitto_passwd -b -c "${MQTT_PASSWD_FILE}" "${MQTT_USERNAME}" "${MQTT_PASSWORD}"
  else
    sudo apt-get install -y mosquitto
    mosquitto_passwd -b -c "${MQTT_PASSWD_FILE}" "${MQTT_USERNAME}" "${MQTT_PASSWORD}"
  fi
  success "MQTT credentials auto-generated."
fi

# --------------------------------------------------------------------------
# 6. Pull images and start the stack
# --------------------------------------------------------------------------
info "Starting SolarSync stack (production mode)..."
cd "${SOLARSYNC_DIR}"

docker compose \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  pull --quiet

docker compose \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  up -d

success "SolarSync is running!"
echo ""
echo "  Open https://solarsync.local in your browser."
echo "  (If solarsync.local doesn't resolve yet, use https://$(hostname -I | awk '{print $1}'))"
echo "  (Accept the self-signed certificate warning on first visit.)"
echo ""
info "Useful commands:"
echo "  View logs:   docker compose -f ${SOLARSYNC_DIR}/docker-compose.yml logs -f"
echo "  Stop:        docker compose -f ${SOLARSYNC_DIR}/docker-compose.yml down"
echo "  Update:      git -C ${INSTALL_DIR} pull && docker compose ... pull && ... up -d"
echo ""
success "Done."
