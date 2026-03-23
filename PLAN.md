# SolarSync Power Manager — Refactor Plan

## Overview

Refactoring from a crypto-miner solar controller into a general-purpose solar-powered appliance scheduler. Users can connect any household appliance (pool pump, EV charger, washing machine, etc.) to a smart plug and have it automatically run when solar panels are producing enough surplus energy.

---

## Stack

| Layer | Technology | Reason |
|---|---|---|
| **API / Business logic** | Python + FastAPI | Keeps existing ICS2000/KaKu code, async-native, auto-docs |
| **Scheduler** | APScheduler (inside FastAPI) | Handles solar polling + appliance switching on a timer |
| **Frontend** | Laravel 11 (PHP) + Blade/Livewire | Beautiful UI, HTTPS out of the box via Nginx, session auth |
| **Database** | SQLite (shared volume) | Zero config, single file, works great on Pi |
| **Smart plug / energy** | ICS2000 (ported), SolarEdge API, MQTT (Zigbee2MQTT) | Provider abstraction — drop-in new providers |
| **Container** | Docker Compose (arm64) | Clean, portable, reproducible |
| **Auto-update** | Watchtower (polls ghcr.io) | Pulls new images automatically |
| **HTTPS** | Nginx reverse proxy + self-signed cert (or Let's Encrypt) | Terminates TLS, routes to Laravel + FastAPI |
| **Auth** | Laravel Sanctum (single household credential) | Secure login, token-based API auth |

---

## Docker Compose Services

```
┌─────────────────────────────────────────┐
│              Nginx (443/80)             │  ← TLS termination, reverse proxy
│    /        → Laravel (port 9000)       │
│    /api/*   → FastAPI (port 8000)       │
└────────────┬──────────────┬────────────┘
             │              │
     ┌───────┴──────┐  ┌────┴──────────┐
     │   Laravel    │  │   FastAPI     │
     │  (PHP-FPM)   │  │   (Python)    │
     │  UI + Auth   │  │  API + Logic  │
     └──────┬───────┘  └────┬──────────┘
            │               │
            └──────┬────────┘
                   │
           ┌───────┴────────┐
           │   SQLite DB    │  (Docker volume)
           └────────────────┘

  + Mosquitto (MQTT broker)  ← for Zigbee2MQTT
  + Zigbee2MQTT              ← for Zigbee devices
  + Watchtower               ← auto-pulls ghcr.io updates
```

---

## Project Structure

```
solarsync/
├── backend/                        # Python FastAPI service
│   ├── main.py
│   ├── core/
│   │   ├── engine.py               # Solar decision logic (turn on/off appliances)
│   │   ├── scheduler.py            # APScheduler: power polling loop
│   │   └── database.py             # SQLModel setup, migrations
│   ├── models/
│   │   └── models.py               # Appliance, Hub, PowerLog, Setting (SQLModel)
│   ├── providers/
│   │   ├── base.py                 # Abstract EnergyProvider, PlugProvider interfaces
│   │   ├── energy/
│   │   │   ├── kaku_p1.py          # KaKu ICS2000 P1 (ported from existing)
│   │   │   └── solaredge.py        # SolarEdge cloud API
│   │   └── plugs/
│   │       ├── kaku.py             # KaKu ICS2000 plug control (ported)
│   │       └── mqtt.py             # MQTT plug control (Zigbee2MQTT / Shelly)
│   ├── api/
│   │   └── routes/
│   │       ├── appliances.py       # CRUD appliances
│   │       ├── hubs.py             # Hub/provider management
│   │       ├── power.py            # Live power status, history
│   │       ├── settings.py         # App settings
│   │       └── onboarding.py       # Onboarding state + steps
│   ├── ics2000/                    # Ported from existing (unchanged logic)
│   │   └── ...
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                       # Laravel 11 app
│   ├── app/
│   │   ├── Http/Controllers/       # Thin controllers, mostly pass-through to API
│   │   └── ...
│   ├── resources/views/
│   │   ├── layouts/app.blade.php   # Base layout with nav
│   │   ├── onboarding/             # Multi-step onboarding wizard
│   │   │   ├── step1-welcome.blade.php
│   │   │   ├── step2-energy-source.blade.php
│   │   │   ├── step3-hub-setup.blade.php
│   │   │   └── step4-first-appliance.blade.php
│   │   ├── dashboard.blade.php     # Live power flow dashboard
│   │   ├── appliances/             # Appliance management (list, create, edit)
│   │   └── settings.blade.php      # Hub/provider settings
│   ├── Dockerfile
│   └── ...
│
├── nginx/
│   ├── nginx.conf                  # Reverse proxy config
│   └── certs/                      # Self-signed cert (generated on first boot)
│
├── docker-compose.yml
├── docker-compose.prod.yml         # Production overrides (ghcr.io image refs)
├── .env.example
└── scripts/
    └── generate-certs.sh           # First-boot self-signed cert generation
```

---

## Core Features

### Onboarding Wizard (first run)
1. Welcome + system check
2. Choose energy source: KaKu P1 / SolarEdge / Both
3. Configure hub credentials (ICS2000 MAC/email/password)
4. Discover smart plugs, assign first appliance
5. Done — redirect to dashboard

### Appliance Model
- Name, icon, assigned plug, watt draw
- Schedule mode: `solar_only` | `solar_preferred` | `time_window` | `manual`
- Time window (optional): e.g. 09:00–18:00
- Priority (1 = highest)
- Status: running / idle / disabled

### Solar Engine (every 5 min)
1. Read current solar surplus from provider
2. Get appliances sorted by priority
3. Turn on appliances whose watt draw fits in surplus (respecting time windows)
4. Turn off appliances when surplus drops below their draw
5. Log power event to DB

### Dashboard
- Live solar production, grid draw, surplus
- Which appliances are currently running
- Timeline/chart of the last 24h
- Manual override toggle per appliance

### Auto-Update (Watchtower)
- Watches `ghcr.io/[username]/solarsync:latest`
- Checks every hour, auto-pulls and restarts containers on new tag

---

## Implementation Phases

- [x] **Phase 1** — Scaffold: Docker Compose + Nginx + SQLite, FastAPI skeleton, Laravel skeleton
  - [x] Create new `solarsync/` directory structure
  - [x] Write `backend/Dockerfile` (Python arm64)
  - [x] Write `frontend/Dockerfile` (PHP-FPM + Laravel)
  - [x] Write `nginx/nginx.conf` (reverse proxy + TLS)
  - [x] Write `scripts/generate-certs.sh` (self-signed cert on first boot)
  - [x] Write `docker-compose.yml` (all services wired together)
  - [x] Write `docker-compose.prod.yml` (ghcr.io image references + Watchtower)
  - [x] Write `.env.example`
  - [x] Bootstrap FastAPI app inside `backend/` (main.py, lifespan, routers)
  - [x] Set up SQLite + SQLModel in backend (models, database.py)
  - [x] Write solar engine + APScheduler (core/engine.py, core/scheduler.py)
  - [x] Write provider abstraction layer (providers/base.py, kaku, mqtt, solaredge)
  - [x] Write all FastAPI route files (appliances, hubs, power, settings, onboarding)
  - [x] Write Mosquitto config
  - [ ] Bootstrap Laravel 11 project inside `frontend/` (Phase 3)

- [x] **Phase 2** — Port Python backend: provider abstraction + FastAPI routes
  - [x] Define abstract `EnergyProvider` and `PlugProvider` interfaces (`providers/base.py`)
  - [x] Port ICS2000 library (`ics2000/`) from existing codebase
  - [x] Implement `KaKuP1Provider` (energy) using ported ICS2000 code
  - [x] Implement `KaKuPlugProvider` (plugs) using ported ICS2000 code
  - [x] Define SQLModel models: `Appliance`, `Hub`, `PowerLog`, `Setting`
  - [x] Implement APScheduler solar engine loop (`core/engine.py`, `core/scheduler.py`)
  - [x] FastAPI routes: appliances CRUD
  - [x] FastAPI routes: hubs management
  - [x] FastAPI routes: live power status + history
  - [x] FastAPI routes: settings
  - [x] FastAPI routes: onboarding state

- [x] **Phase 3** — Laravel: auth + onboarding wizard
  - [x] Install + configure Laravel Sanctum
  - [x] Build login page (single household credential)
  - [x] Onboarding step 1: Welcome + system check
  - [x] Onboarding step 2: Choose energy source
  - [x] Onboarding step 3: Hub credentials + plug discovery
  - [x] Onboarding step 4: Add first appliance
  - [x] Onboarding completion + redirect to dashboard

- [x] **Phase 4** — Laravel: dashboard + appliance pages + settings
  - [x] Dashboard: live power flow (solar / grid / surplus)
  - [x] Dashboard: running appliances list
  - [x] Dashboard: 24h power history chart
  - [x] Dashboard: manual override toggle per appliance
  - [x] Appliances: list page
  - [x] Appliances: create / edit form (name, icon, watt draw, schedule mode, time window, priority)
  - [x] Appliances: delete + enable/disable
  - [x] Settings: hub/provider configuration page

- [x] **Phase 5** — Additional providers
  - [x] Implement `SolarEdgeProvider` (energy) — SolarEdge cloud API
  - [x] Implement `MqttPlugProvider` — Zigbee2MQTT + Mosquitto MQTT broker
  - [x] Add Mosquitto + Zigbee2MQTT services to docker-compose
  - [x] Expose provider selection in onboarding + settings UI

- [x] **Phase 6** — CI/CD + remote updates
  - [x] GitHub Actions workflow: build arm64 Docker images + push to ghcr.io on tag
  - [x] Add Watchtower service to `docker-compose.prod.yml`
  - [x] Document update process in README
  - [x] Write `scripts/install.sh` (first-time Pi setup: install Docker, clone repo, start stack)
