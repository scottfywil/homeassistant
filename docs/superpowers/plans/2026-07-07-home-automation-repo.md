# Home Automation Repo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the complete git-managed Home Assistant configuration repo — HA config, ESPHome templates, Zigbee2MQTT reference config, runbooks, and CI — per the approved spec.

**Architecture:** Repo root IS the HA `/config` directory (required by the Git Pull add-on, which clones into `/config`). ESPHome configs use a shared `common/` package via `packages:` + substitutions. CI validates YAML lint, HA config, and ESPHome configs on every push.

**Tech Stack:** Home Assistant OS + add-ons (Mosquitto, Zigbee2MQTT, ESPHome, Git Pull, Tailscale), ESPHome YAML (esp-idf framework), GitHub Actions.

**Layout note (deviation from spec):** Spec showed a `config/` subdirectory. The Git Pull add-on pulls the repo directly into `/config`, so HA config lives at repo root instead. `esphome/`, `zigbee2mqtt/`, `docs/`, `.github/` sit alongside — harmless inside `/config`.

**Testing note:** This is a configuration repo — validation replaces TDD. Each task ends with a commit; Task 10 runs yamllint + `esphome config` locally, and CI re-runs everything on push.

---

### Task 1: Scaffolding — .gitignore, .yamllint, secrets example, README

**Files:**
- Create: `.gitignore`, `.yamllint`, `secrets.yaml.example`, `README.md`

- [ ] **Step 1: Create `.gitignore`** — must exclude every HA runtime artifact, since `/config` on the box becomes this git checkout:

```gitignore
# Secrets — NEVER commit
secrets.yaml
esphome/secrets.yaml
esphome/devices/secrets.yaml
zigbee2mqtt/secret.yaml

# Home Assistant runtime state
.storage/
.cloud/
.HA_VERSION
.uuid
home-assistant.log*
home-assistant_v2.db*
zigbee.db*
deps/
tts/
backups/
blueprints/
image/
www/community/

# ESPHome build artifacts
esphome/.esphome/
.esphome/

# OS / editor
.DS_Store
Thumbs.db
__pycache__/
```

- [ ] **Step 2: Create `.yamllint`** (relaxed rules for HA-style YAML):

```yaml
extends: default

ignore: |
  .storage/

rules:
  line-length: disable
  document-start: disable
  truthy: disable
  comments:
    min-spaces-from-content: 1
  braces:
    max-spaces-inside: 1
```

- [ ] **Step 3: Create `secrets.yaml.example`** — every key documented; the example API key is valid base64 so `esphome config` passes in CI, but MUST be regenerated for real use:

```yaml
# Copy to secrets.yaml (HA) and esphome/devices/secrets.yaml (ESPHome), then fill in.
# NEVER commit the real files — both are gitignored.

# --- WiFi (ESPHome boards) ---
wifi_ssid: "MyNetwork"
wifi_password: "wifi-password-here"
fallback_ap_password: "fallback-ap-password"

# --- ESPHome ---
# Generate a real key: https://esphome.io/components/api.html  (32-byte base64)
api_encryption_key: "aGVsbG8tZ2VuZXJhdGUtYS1yZWFsLWtleS1oZXJlIQ=="
ota_password: "ota-password-here"

# --- MQTT (Mosquitto add-on user) ---
mqtt_username: "mqtt"
mqtt_password: "mqtt-password-here"
```

- [ ] **Step 4: Create `README.md`** with repo overview, layout table, quick-start pointing at `docs/` runbooks, and secrets warning. Content per the executed version (overview of stack: HAOS + Mosquitto + Zigbee2MQTT + ESPHome + Git Pull + Tailscale + Nabu Casa; layout matching this plan; link each runbook).

- [ ] **Step 5: Commit**

```bash
git add .gitignore .yamllint secrets.yaml.example README.md
git commit -m "Add scaffolding: gitignore, yamllint, secrets example, README"
```

### Task 2: Home Assistant core config

**Files:**
- Create: `configuration.yaml`, `automations.yaml`, `scripts.yaml`, `scenes.yaml`, `packages/system.yaml`

- [ ] **Step 1: Create `configuration.yaml`**:

```yaml
# Core stays slim — features live in packages/.
default_config:

homeassistant:
  packages: !include_dir_named packages

# UI-created automations/scripts/scenes (keeps the UI editors working)
automation ui: !include automations.yaml
script ui: !include scripts.yaml
scene ui: !include scenes.yaml

# Git-managed YAML dashboard alongside the default UI dashboard
lovelace:
  mode: storage
  dashboards:
    yaml-overview:
      mode: yaml
      title: Overview (Git)
      icon: mdi:home-automation
      filename: dashboards/overview.yaml
```

- [ ] **Step 2: Create the UI include files** — `automations.yaml` containing exactly `[]`, `scripts.yaml` containing `{}`, `scenes.yaml` containing `[]`.

- [ ] **Step 3: Create `packages/system.yaml`**:

```yaml
# System housekeeping
recorder:
  purge_keep_days: 14

automation:
  - alias: "System - Notify on Home Assistant start"
    id: system_notify_ha_start
    triggers:
      - trigger: homeassistant
        event: start
    actions:
      - action: persistent_notification.create
        data:
          title: "Home Assistant started"
          message: "Config loaded {{ now().strftime('%Y-%m-%d %H:%M') }}."
```

- [ ] **Step 4: Commit**

```bash
git add configuration.yaml automations.yaml scripts.yaml scenes.yaml packages/system.yaml
git commit -m "Add HA core config with packages structure"
```

### Task 3: Feature packages — lighting and climate

**Files:**
- Create: `packages/lighting.yaml`, `packages/climate.yaml`

- [ ] **Step 1: Create `packages/lighting.yaml`** — motion lighting wired to the office room-sensor board (entities exist once the board is adopted; automations are inert until then):

```yaml
# Motion-activated lighting driven by the office-sensor ESP32 board.
# Clone this pattern per room; swap entity IDs.
automation:
  - alias: "Lighting - Office on motion when dark"
    id: lighting_office_motion_on
    triggers:
      - trigger: state
        entity_id: binary_sensor.office_sensor_motion
        to: "on"
    conditions:
      - condition: numeric_state
        entity_id: sensor.office_sensor_illuminance
        below: 40
    actions:
      - action: light.turn_on
        target:
          entity_id: light.office

  - alias: "Lighting - Office off after 10 min no motion"
    id: lighting_office_motion_off
    triggers:
      - trigger: state
        entity_id: binary_sensor.office_sensor_motion
        to: "off"
        for: "00:10:00"
    actions:
      - action: light.turn_off
        target:
          entity_id: light.office
```

- [ ] **Step 2: Create `packages/climate.yaml`** — whole-home average temperature template sensor over the room-sensor boards:

```yaml
# Indoor climate rollups from ESP32 room sensors.
template:
  - sensor:
      - name: "Indoor average temperature"
        unique_id: indoor_average_temperature
        unit_of_measurement: "°F"
        device_class: temperature
        state_class: measurement
        state: >
          {% set temps = [
              states('sensor.office_sensor_temperature'),
            ] | reject('in', ['unknown', 'unavailable', 'none']) | map('float') | list %}
          {{ (temps | average) | round(1) if temps else none }}
        availability: >
          {{ [states('sensor.office_sensor_temperature')]
             | reject('in', ['unknown', 'unavailable', 'none']) | list | count > 0 }}
```

- [ ] **Step 3: Commit**

```bash
git add packages/lighting.yaml packages/climate.yaml
git commit -m "Add lighting and climate feature packages"
```

### Task 4: Git-managed dashboard

**Files:**
- Create: `dashboards/overview.yaml`

- [ ] **Step 1: Create `dashboards/overview.yaml`** — one view with climate, ESP32 device health, and lighting sections (entity cards referencing the template + board entities defined above).

```yaml
title: Overview (Git)
views:
  - title: Home
    path: home
    icon: mdi:home
    sections:
      - type: grid
        cards:
          - type: heading
            heading: Climate
          - type: entity
            entity: sensor.indoor_average_temperature
            name: Indoor Average
          - type: entities
            title: Office
            entities:
              - sensor.office_sensor_temperature
              - sensor.office_sensor_humidity
              - sensor.office_sensor_illuminance
              - binary_sensor.office_sensor_motion
      - type: grid
        cards:
          - type: heading
            heading: Controls
          - type: entities
            title: Relays & LEDs
            entities:
              - switch.garage_relay_relay_1
              - light.desk_leds_led_strip
      - type: grid
        cards:
          - type: heading
            heading: Device Health
          - type: entities
            title: ESP32 Boards
            entities:
              - sensor.office_sensor_wifi_signal
              - sensor.garage_relay_wifi_signal
              - sensor.ble_proxy_hallway_wifi_signal
              - sensor.desk_leds_wifi_signal
    type: sections
```

- [ ] **Step 2: Commit**

```bash
git add dashboards/overview.yaml
git commit -m "Add git-managed overview dashboard"
```

### Task 5: ESPHome shared packages

**Files:**
- Create: `esphome/common/base.yaml`, `esphome/common/ble_proxy.yaml`

- [ ] **Step 1: Create `esphome/common/base.yaml`** — everything every board shares; consumed via `packages:` with substitutions:

```yaml
# Shared base for all boards. Include from a device file:
#   substitutions:
#     device_name: my-board
#     friendly_name: My Board
#     board: esp32dev
#   packages:
#     base: !include ../common/base.yaml
esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}

esp32:
  board: ${board}
  framework:
    type: esp-idf

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  ap:
    ssid: ${device_name}
    password: !secret fallback_ap_password

captive_portal:

api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
    password: !secret ota_password

logger:

sensor:
  - platform: wifi_signal
    name: WiFi Signal
    update_interval: 120s
  - platform: uptime
    name: Uptime
    update_interval: 300s

text_sensor:
  - platform: wifi_info
    ip_address:
      name: IP Address

button:
  - platform: restart
    name: Restart
```

- [ ] **Step 2: Create `esphome/common/ble_proxy.yaml`**:

```yaml
# Add to any esp32 board with free radio time to extend BLE coverage.
esp32_ble_tracker:
  scan_parameters:
    active: true

bluetooth_proxy:
  active: true
```

- [ ] **Step 3: Commit**

```bash
git add esphome/common/
git commit -m "Add ESPHome shared base and BLE proxy packages"
```

### Task 6: ESPHome device templates (4 boards)

**Files:**
- Create: `esphome/devices/office-sensor.yaml`, `esphome/devices/garage-relay.yaml`, `esphome/devices/ble-proxy-hallway.yaml`, `esphome/devices/led-desk.yaml`

- [ ] **Step 1: Create `esphome/devices/office-sensor.yaml`** (room multi-sensor: BME280 temp/humidity/pressure, BH1750 lux, PIR motion, doubles as BLE proxy):

```yaml
substitutions:
  device_name: office-sensor
  friendly_name: Office Sensor
  board: esp32dev

packages:
  base: !include ../common/base.yaml
  ble: !include ../common/ble_proxy.yaml

i2c:
  sda: GPIO21
  scl: GPIO22
  scan: true

sensor:
  - platform: bme280_i2c
    address: 0x76
    update_interval: 60s
    temperature:
      name: Temperature
    humidity:
      name: Humidity
    pressure:
      name: Pressure
  - platform: bh1750
    name: Illuminance
    address: 0x23
    update_interval: 30s

binary_sensor:
  - platform: gpio
    pin: GPIO27
    name: Motion
    device_class: motion
```

- [ ] **Step 2: Create `esphome/devices/garage-relay.yaml`** (relay + physical fallback button, relays stay OFF on boot for safety):

```yaml
substitutions:
  device_name: garage-relay
  friendly_name: Garage Relay
  board: esp32dev

packages:
  base: !include ../common/base.yaml

switch:
  - platform: gpio
    pin: GPIO26
    name: Relay 1
    id: relay_1
    restore_mode: ALWAYS_OFF

binary_sensor:
  - platform: gpio
    pin:
      number: GPIO33
      mode: INPUT_PULLUP
      inverted: true
    name: Button 1
    filters:
      - delayed_on: 10ms
    on_press:
      - switch.toggle: relay_1
```

- [ ] **Step 3: Create `esphome/devices/ble-proxy-hallway.yaml`** (pure BLE range extender — the ~10-line new-board case):

```yaml
substitutions:
  device_name: ble-proxy-hallway
  friendly_name: BLE Proxy Hallway
  board: esp32dev

packages:
  base: !include ../common/base.yaml
  ble: !include ../common/ble_proxy.yaml
```

- [ ] **Step 4: Create `esphome/devices/led-desk.yaml`** (WS2812B addressable strip with effects):

```yaml
substitutions:
  device_name: led-desk
  friendly_name: Desk LEDs
  board: esp32dev

packages:
  base: !include ../common/base.yaml

light:
  - platform: esp32_rmt_led_strip
    name: LED Strip
    pin: GPIO16
    num_leds: 60
    chipset: WS2812
    rgb_order: GRB
    restore_mode: RESTORE_DEFAULT_OFF
    effects:
      - addressable_rainbow:
      - addressable_color_wipe:
      - addressable_twinkle:
      - addressable_scan:
      - pulse:
```

- [ ] **Step 5: Commit**

```bash
git add esphome/devices/
git commit -m "Add ESPHome device templates: room sensor, relay, BLE proxy, LED"
```

### Task 7: Zigbee2MQTT reference config

**Files:**
- Create: `zigbee2mqtt/configuration.yaml`

- [ ] **Step 1: Create `zigbee2mqtt/configuration.yaml`** — reference config copied into the Z2M add-on data dir per runbook 02 (Z2M reads `!secret` from its own `secret.yaml`):

```yaml
# Reference config for the Zigbee2MQTT add-on.
# Copy into the add-on's data directory; create secret.yaml beside it
# with mqtt_username / mqtt_password (see secrets.yaml.example).
homeassistant:
  enabled: true

mqtt:
  base_topic: zigbee2mqtt
  server: mqtt://core-mosquitto:1883
  user: '!secret mqtt_username'
  password: '!secret mqtt_password'

serial:
  port: /dev/ttyACM0
  adapter: ember  # Sonoff ZBDongle-E (EFR32). Use 'zstack' for ZBDongle-P/CC2652.

frontend:
  enabled: true
  port: 8099

advanced:
  channel: 20
  network_key: GENERATE
  last_seen: ISO_8601

permit_join: false
```

- [ ] **Step 2: Commit**

```bash
git add zigbee2mqtt/configuration.yaml
git commit -m "Add Zigbee2MQTT reference configuration"
```

### Task 8: CI workflow

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Create `.github/workflows/ci.yml`** — three jobs: yamllint, HA config check (frenck action, secrets from example), ESPHome validation of every device file:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  yamllint:
    name: YAML lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install yamllint
      - run: yamllint .

  ha-config:
    name: Home Assistant config check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Provide secrets from example
        run: cp secrets.yaml.example secrets.yaml
      - name: Check configuration
        uses: frenck/action-home-assistant@v1
        with:
          path: "."
          version: stable

  esphome:
    name: ESPHome config check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install esphome
      - name: Provide secrets from example
        run: cp secrets.yaml.example esphome/devices/secrets.yaml
      - name: Validate all device configs
        run: |
          set -e
          for f in esphome/devices/*.yaml; do
            case "$f" in *secrets*) continue;; esac
            echo "== $f"
            esphome config "$f" > /dev/null
          done
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "Add CI: yamllint, HA config check, ESPHome validation"
```

### Task 9: Runbooks

**Files:**
- Create: `docs/01-flash-haos.md`, `docs/02-addons.md`, `docs/03-nabu-casa-alexa.md`, `docs/04-pairing-devices.md`, `docs/05-new-esp32-board.md`, `docs/06-backups.md`

- [ ] **Step 1: Write the six runbooks.** Each is a complete step-by-step guide:
  - `01-flash-haos.md` — hardware options (N100 mini PC vs Pi 4/5), imaging HAOS, first boot, onboarding, static IP/DHCP reservation.
  - `02-addons.md` — install order and full configuration for Mosquitto (+ MQTT user), Zigbee2MQTT (dongle, config from `zigbee2mqtt/`), ESPHome, Git Pull (repo URL, deployment key, auto-restart), Tailscale, Studio Code Server, Samba.
  - `03-nabu-casa-alexa.md` — subscribe, link Alexa skill, entity exposure strategy (expose deliberately, not everything), voice naming tips.
  - `04-pairing-devices.md` — Zigbee pairing via Z2M frontend (permit_join), WiFi device integrations (Tuya/Kasa/Wyze), cloud devices (Ring/Nest/ecobee), naming conventions (`<room>_<device>`).
  - `05-new-esp32-board.md` — clone a template, first USB flash via ESPHome dashboard, OTA thereafter, secrets placement, adding to dashboard/packages.
  - `06-backups.md` — HAOS automatic backups, schedule, Samba offload, restore procedure.

- [ ] **Step 2: Commit**

```bash
git add docs/
git commit -m "Add setup and operations runbooks"
```

### Task 10: Local validation

- [ ] **Step 1: Run yamllint locally**

Run: `pip install yamllint && yamllint .` (from repo root)
Expected: exit 0, no output.

- [ ] **Step 2: Validate ESPHome configs locally**

Run:
```bash
pip install esphome
cp secrets.yaml.example esphome/devices/secrets.yaml
for f in esphome/devices/*.yaml; do case "$f" in *secrets*) continue;; esac; esphome config "$f" > /dev/null && echo "OK $f"; done
rm esphome/devices/secrets.yaml
```
Expected: `OK` for all four device files.

- [ ] **Step 3: Fix any findings, commit fixes**

### Task 11: Push and hand off

- [ ] **Step 1: Push branch** — direct push to `main` is blocked by policy in this session; push `initial-setup` (first branch pushed to an empty repo becomes its default; user merges/renames as desired):

```bash
git push -u origin main:initial-setup
```

- [ ] **Step 2: Report** — summarize repo URL, branch state, CI status, and the physical-world steps only the user can do (buy hardware, flash HAOS, subscribe to Nabu Casa, pair devices).
