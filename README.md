# SolarSync Power Manager

Automatically run household appliances (pool pump, EV charger, washing machine, …) when your solar panels are producing surplus energy.

Built for **Raspberry Pi 4/5 (arm64)**, but runs on any Linux machine with Docker.

---

## Features

- **Live dashboard** — solar production, grid draw, surplus, running appliances
- **24 h power chart** — see where your energy went
- **Smart scheduling** — `solar_only`, `solar_preferred`, `time_window`, or `manual` per appliance
- **Manual override** — force any appliance on/off from the dashboard
- **Multiple energy sources** — KaKu P1 meter and/or SolarEdge cloud API
- **Multiple plug types** — KaKu ICS2000 smart plugs and Zigbee devices via Zigbee2MQTT
- **Automatic updates** — Watchtower polls ghcr.io and restarts containers on new releases
- **HTTPS by default** — Nginx with a self-signed certificate (or bring your own)

---

## Quick Install (Raspberry Pi)

```bash
curl -fsSL https://raw.githubusercontent.com/Mel-Raeven/SolarSync-Power-Manager/main/solarsync/scripts/install.sh | bash
```

The script will:
1. Install Docker (if missing)
2. Clone this repository to `~/solarsync`
3. Prompt for a username and password for the web interface
4. Generate a self-signed TLS certificate
5. Pull the latest images from ghcr.io and start all services

Open `https://<pi-ip-address>` in your browser and follow the onboarding wizard.

---

## Manual Setup

### 1. Clone

```bash
git clone https://github.com/Mel-Raeven/SolarSync-Power-Manager.git ~/solarsync
cd ~/solarsync/solarsync
```

### 2. Configure

```bash
cp .env.example .env
nano .env          # fill in your credentials and energy provider settings
```

Key variables:

| Variable | Description |
|---|---|
| `SOLARSYNC_USERNAME` | Web login username (default: `admin`) |
| `SOLARSYNC_PASSWORD` | Web login password — **change this** |
| `KAKU_MAC_ADDRESS` | MAC address of your ICS2000 hub |
| `KAKU_EMAIL` | KaKu account email |
| `KAKU_PASSWORD` | KaKu account password |
| `SOLAREDGE_API_KEY` | SolarEdge API key (optional) |
| `SOLAREDGE_SITE_ID` | SolarEdge site ID (optional) |
| `POLL_INTERVAL_SECONDS` | How often the solar engine runs (default: `300`) |

### 3. Generate TLS certificate

```bash
bash scripts/generate-certs.sh
```

### 4. Start

**Development** (builds images locally):
```bash
docker compose up -d
```

**Production** (pulls from ghcr.io, includes Watchtower):
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Optional: Zigbee devices (Zigbee2MQTT)

If you have a Zigbee USB adapter, start the Zigbee2MQTT service:

```bash
docker compose --profile zigbee up -d
```

Edit `zigbee2mqtt/configuration.yaml` to set your USB device path and MQTT credentials.

---

## Updating

Watchtower automatically checks ghcr.io every hour and restarts containers when a new image is available. No manual action required.

To update manually:

```bash
cd ~/solarsync
git pull
docker compose -f solarsync/docker-compose.yml -f solarsync/docker-compose.prod.yml pull
docker compose -f solarsync/docker-compose.yml -f solarsync/docker-compose.prod.yml up -d
```

---

## Architecture

```
Browser ──HTTPS──► Nginx (443)
                     │
          ┌──────────┴──────────┐
          │                     │
     Laravel (PHP-FPM)     FastAPI (Python)
     UI + Auth              Solar engine + REST API
          │                     │
          └──────────┬──────────┘
                     │
               SQLite (volume)

  + Mosquitto (MQTT broker)
  + Zigbee2MQTT (optional, --profile zigbee)
  + Watchtower (auto-updates from ghcr.io)
```

| Layer | Technology |
|---|---|
| Frontend | Laravel 11 + Blade + Tailwind CSS |
| Backend API | Python + FastAPI |
| Scheduler | APScheduler (inside FastAPI) |
| Database | SQLite via SQLModel |
| Auth | Laravel Sanctum (single household credential) |
| Container | Docker Compose (arm64) |
| TLS | Nginx reverse proxy + self-signed cert |
| Auto-update | Watchtower |

---

## Releasing a New Version

1. Merge changes to `main`
2. Create and push a version tag:
   ```bash
   git tag v1.2.3
   git push origin v1.2.3
   ```
3. GitHub Actions builds arm64 Docker images and pushes them to ghcr.io
4. Watchtower on your Pi picks up the new `latest` tag within the hour

---

## Acknowledgements

- [KaKu core](https://github.com/Stijn-Jacobs/ICS2000-Python) — original ICS2000 Python library

---

## License

Copyright (c) 2026. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution, modification, or use of this software, in whole or in part, is strictly prohibited.
