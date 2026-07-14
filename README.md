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
├── esphome/                # one YAML per physical ESP32 board
│   └── common/             # shared board packages (base, ble_proxy)
├── hardware/enclosure/     # 3D-printed multisensor case + Amazon BOM
├── docs/                   # runbooks (start at 01) + Z2M reference config
├── secrets.yaml.example    # every required secret, documented
└── .github/workflows/      # CI
```

(`zigbee2mqtt/` exists on the box but is gitignored — it's the add-on's
runtime data dir and holds the generated network key.)

## Quick start

Follow the runbooks in order:

1. [Flash HAOS and onboard](docs/01-flash-haos.md)
2. [Install and configure add-ons](docs/02-addons.md)
3. [Nabu Casa + Alexa](docs/03-nabu-casa-alexa.md)
4. [Pair devices](docs/04-pairing-devices.md)
5. [Build a new ESP32 board](docs/05-new-esp32-board.md)
6. [Backups](docs/06-backups.md)
7. [Home layout and coverage plan](docs/07-home-layout.md)
8. [Presence sensors: build plan and BOM](docs/08-presence-sensors.md)

## Secrets

Copy `secrets.yaml.example` to `secrets.yaml` and fill in real values on the
HA box (and to `esphome/secrets.yaml` wherever you build firmware).
Real secrets files are gitignored — never commit them. Regenerate the ESPHome
API key (`openssl rand -base64 32`); the example value is a placeholder.

## Adding an ESP32 board

Every board is ~10 lines of YAML on top of `esphome/common/base.yaml`
(WiFi + fallback AP, encrypted API, OTA, diagnostics). See
[docs/05-new-esp32-board.md](docs/05-new-esp32-board.md). Once the board is
adopted by HA it can be exposed to Alexa through Nabu Casa like any entity.
