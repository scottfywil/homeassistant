# Home Automation System — Design Spec

**Date:** 2026-07-07
**Repo:** https://github.com/scottfywil/homeassistant
**Status:** Approved

## Goal

A Home Assistant-based home automation system that unifies an existing Amazon
Alexa (Echo) setup and assorted third-party smart devices under one local-first
controller, extensible with custom ESP32 boards. All configuration lives in
this git repository as the source of truth. This is a personal project,
unrelated to HubWise systems.

## Decisions (locked)

| Decision | Choice |
|---|---|
| HA platform | Home Assistant OS (generic x86-64) bare-metal on an HP EliteDesk 800 G3 Desktop Mini (512 GB), wiping Windows |
| Zigbee | Zigbee2MQTT + Mosquitto add-ons; "Zigbee 3.0 USB Dongle Plus" MG24 coordinator (Silicon Labs EFR32MG24, `ember` adapter) |
| Alexa | Nabu Casa (Home Assistant Cloud, $6.50/mo) — exposes HA entities to Alexa, provides remote access |
| ESP32 firmware | ESPHome (YAML-defined, OTA, auto-discovery) |
| Deploy flow | HA pulls from GitHub (Git Pull add-on); repo is source of truth |
| Admin access | Tailscale add-on (user runs a personal tailnet) alongside Nabu Casa |
| CI | GitHub Actions: yamllint + HA config check + ESPHome config validation |

## Device landscape

- **WiFi devices** (Tuya, Kasa, Wyze plugs/bulbs): native HA integrations,
  configured via UI (config entries), documented in runbooks.
- **Zigbee devices** (Hue, Aqara, IKEA, SmartThings sensors): paired through
  Zigbee2MQTT; device settings tracked in `zigbee2mqtt/configuration.yaml`.
- **Cloud-only devices** (Ring/Nest/ecobee class): native HA cloud
  integrations via UI, documented in runbooks.
- **Custom ESP32 boards**: ESPHome configs in `esphome/devices/`, built on a
  shared `esphome/common/` package.
- **Alexa Echos**: voice front-end via Nabu Casa entity exposure; optionally
  Alexa Media Player integration later for TTS announcements.

## Architecture

```
GitHub repo ──(Git Pull add-on)──> HAOS box
                                     ├── Home Assistant Core (config/)
                                     ├── Mosquitto (MQTT broker)
                                     ├── Zigbee2MQTT ── MG24 dongle ── Zigbee devices
                                     ├── ESPHome ──(OTA/API)── ESP32 boards
                                     ├── Tailscale (admin access)
                                     └── Nabu Casa cloud ── Alexa / remote UI
```

Local-first: automations, Zigbee, and ESPHome function without internet.
Only Alexa voice and cloud-device integrations require WAN.

## Repo layout

```
homeassistant/
├── config/                      # Home Assistant configuration
│   ├── configuration.yaml       # slim core; default_config + packages include
│   ├── packages/                # one YAML per feature area
│   └── dashboards/              # Lovelace YAML dashboards
├── esphome/
│   ├── common/                  # shared packages: wifi/api/ota/diagnostics, ble proxy
│   └── devices/                 # one YAML per physical board
├── zigbee2mqtt/                 # Z2M configuration (no secrets)
├── docs/                        # runbooks (see below)
├── .github/workflows/ci.yml     # validation pipeline
├── secrets.yaml.example         # every required secret, documented
└── README.md
```

## ESP32 board templates (ESPHome)

Shared `common/base.yaml`: WiFi (+ fallback AP), native API with encryption,
OTA, web server, diagnostic sensors (uptime, WiFi signal, IP), restart button.
Boards include it via ESPHome `packages:` with substitutions so a new board is
~10 lines.

1. **room-sensor** — BME280 (temp/humidity/pressure) or SHT31, PIR motion,
   BH1750 lux. I2C + one GPIO.
2. **relay-controller** — 1–4 relay channels with physical fallback buttons,
   safe restore modes (relays off on boot) for garage/irrigation use.
3. **ble-proxy** — ESP32 as Bluetooth proxy extending BLE coverage; minimal
   config on top of base.
4. **led-controller** — WS2812B/addressable strip with effects, presets
   exposed to HA (and thus Alexa).

Bluetooth proxy is also enabled on other boards where the chip allows.

## Secrets

`secrets.yaml` (and `esphome/secrets.yaml` symlink/copy) are gitignored.
`secrets.yaml.example` documents every key: WiFi SSID/password, ESPHome API
encryption key, OTA password, MQTT credentials, latitude/longitude/elevation.

## Deploy flow

1. Edit YAML locally (or via PR), push to `main`.
2. CI validates (yamllint, `home-assistant/core` check_config, `esphome config`).
3. Git Pull add-on on the HAOS box fetches `main` and triggers HA reload/restart.
4. ESPHome firmware changes are applied from the ESPHome dashboard (OTA) —
   documented as a manual step in the runbook.

## Runbooks (docs/)

- `01-flash-haos.md` — image the x86-64 PC bare-metal, first boot, onboarding
- `02-addons.md` — install/configure Mosquitto, Zigbee2MQTT, ESPHome,
  Git Pull, Tailscale, Studio Code Server, Samba
- `03-nabu-casa-alexa.md` — subscribe, link Alexa skill, entity exposure rules
- `04-pairing-devices.md` — Zigbee pairing, WiFi/cloud integration setup
- `05-new-esp32-board.md` — clone a template, first USB flash, OTA thereafter
- `06-backups.md` — HAOS backup schedule, Samba, restore procedure

## Error handling / resilience

- ESP32 boards: static IPs, fallback hotspot, `restore_mode: ALWAYS_OFF` on
  safety-relevant relays, watchdog via native API reconnect.
- HA: automation `mode` set deliberately; packages keep failures isolated.
- Backups before Git Pull-triggered restarts (HAOS automatic backup on
  add-on update; scheduled full backups documented).
- CI blocks broken config from reaching the box.

## Testing

- CI: yamllint, HA `check_config` in the official container, `esphome config`
  compile-check for every device file.
- Manual smoke tests per runbook after first deploy: Zigbee pair one device,
  flash one ESP32, verify Alexa sees an exposed entity.

## Out of scope (YAGNI)

- Custom C++ ESPHome components (revisit if a board needs one)
- DIY AWS Lambda Alexa skill (Nabu Casa chosen)
- Camera/NVR (Frigate) — future project
- Zigbee/Z-Wave beyond the single Zigbee coordinator
- Multi-instance / remote sites
