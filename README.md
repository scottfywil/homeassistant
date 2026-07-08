# Home Assistant — Home Automation Config

Git-managed configuration for a Home Assistant-based home automation system:
one local-first controller unifying Alexa, third-party smart devices (WiFi,
Zigbee, cloud), and custom ESP32 boards running ESPHome.

**This repo IS the Home Assistant `/config` directory.** The Git Pull add-on
clones it onto the HAOS box; push to GitHub and the box updates itself.

## Stack

| Layer | Choice |
|---|---|
| Platform | Home Assistant OS (generic x86-64) bare-metal on an HP EliteDesk 800 G3 Desktop Mini |
| Zigbee | Zigbee2MQTT + Mosquitto add-ons, "Zigbee 3.0 USB Dongle Plus" MG24 (EFR32MG24) coordinator |
| ESP32 boards | ESPHome (YAML firmware, OTA, auto-discovery) |
| Voice / remote | Nabu Casa (Home Assistant Cloud) → Alexa |
| Admin access | Tailscale add-on |
| Deploy | Git Pull add-on (GitHub → `/config`) |
| CI | yamllint + HA config check + ESPHome validation on every push |

## Layout

```
├── configuration.yaml      # slim core; features live in packages/
├── packages/               # one YAML per feature area (system, lighting, climate…)
├── dashboards/             # git-managed Lovelace dashboards
├── esphome/
│   ├── common/             # shared board packages (base, ble_proxy)
│   └── devices/            # one YAML per physical ESP32 board
├── zigbee2mqtt/            # reference config for the Z2M add-on
├── docs/                   # runbooks (start at 01)
├── secrets.yaml.example    # every required secret, documented
└── .github/workflows/      # CI
```

## Quick start

Follow the runbooks in order:

1. [Flash HAOS and onboard](docs/01-flash-haos.md)
2. [Install and configure add-ons](docs/02-addons.md)
3. [Nabu Casa + Alexa](docs/03-nabu-casa-alexa.md)
4. [Pair devices](docs/04-pairing-devices.md)
5. [Build a new ESP32 board](docs/05-new-esp32-board.md)
6. [Backups](docs/06-backups.md)

## Secrets

Copy `secrets.yaml.example` to `secrets.yaml` and fill in real values on the
HA box (and to `esphome/devices/secrets.yaml` wherever you build firmware).
Real secrets files are gitignored — never commit them. Regenerate the ESPHome
API key (`openssl rand -base64 32`); the example value is a placeholder.

## Adding an ESP32 board

Every board is ~10 lines of YAML on top of `esphome/common/base.yaml`
(WiFi + fallback AP, encrypted API, OTA, diagnostics). See
[docs/05-new-esp32-board.md](docs/05-new-esp32-board.md). Once the board is
adopted by HA it can be exposed to Alexa through Nabu Casa like any entity.
