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
# 4. Create .env from .env.example (if not already present)
# --------------------------------------------------------------------------
ENV_FILE="${SOLARSYNC_DIR}/.env"
EXAMPLE_FILE="${SOLARSYNC_DIR}/.env.example"

if [[ -f "${ENV_FILE}" ]]; then
  info ".env already exists — skipping (edit ${ENV_FILE} manually if needed)."
else
  if [[ ! -f "${EXAMPLE_FILE}" ]]; then
    error ".env.example not found at ${EXAMPLE_FILE}"
  fi
  cp "${EXAMPLE_FILE}" "${ENV_FILE}"
  success "Created ${ENV_FILE} from .env.example"

  # Prompt for the most important values
  echo ""
  warn "Please configure the following required values in ${ENV_FILE}:"
  echo ""

  read -rp "  SolarSync username (for web login) [admin]: " SS_USER
  SS_USER="${SS_USER:-admin}"

  read -rsp "  SolarSync password: " SS_PASS
  echo ""
  if [[ -z "${SS_PASS}" ]]; then
    error "Password cannot be empty."
  fi

  # Replace placeholders in .env
  sed -i "s|^SOLARSYNC_USERNAME=.*|SOLARSYNC_USERNAME=${SS_USER}|" "${ENV_FILE}"
  sed -i "s|^SOLARSYNC_PASSWORD=.*|SOLARSYNC_PASSWORD=${SS_PASS}|" "${ENV_FILE}"

  success "Credentials saved to ${ENV_FILE}"
  echo ""
  warn "Review ${ENV_FILE} to configure your energy provider (KaKu P1 / SolarEdge)."
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
echo "  Open https://$(hostname -I | awk '{print $1}') in your browser."
echo "  (Accept the self-signed certificate warning.)"
echo ""
info "Useful commands:"
echo "  View logs:   docker compose -f ${SOLARSYNC_DIR}/docker-compose.yml logs -f"
echo "  Stop:        docker compose -f ${SOLARSYNC_DIR}/docker-compose.yml down"
echo "  Update:      git -C ${INSTALL_DIR} pull && docker compose ... pull && ... up -d"
echo ""
success "Done."
