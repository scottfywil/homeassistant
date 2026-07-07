# 05 — Building a New ESP32 Board

Every board is a small YAML file on top of the shared base package.
`esphome/common/base.yaml` provides WiFi (+ fallback hotspot), encrypted
native API, OTA updates, diagnostics (WiFi signal, uptime, IP), and a
restart button. Boards auto-discover in HA once online.

## 1. Create the config

Copy the closest template in `esphome/devices/` and adjust:

```yaml
substitutions:
  device_name: kitchen-sensor      # lowercase, hyphens — becomes hostname
  friendly_name: Kitchen Sensor    # becomes the HA device name / entity prefix
  board: esp32dev                  # or esp32-c3-devkitm-1, etc.

packages:
  base: !include ../common/base.yaml
  ble: !include ../common/ble_proxy.yaml   # drop if the board is RF-busy

# ... sensors/switches/lights for this board
```

Templates:

| Template | Use for |
|---|---|
| `office-sensor.yaml` | Room sensing: BME280 + BH1750 + PIR |
| `garage-relay.yaml` | Switching things safely (relays off on boot) |
| `ble-proxy-hallway.yaml` | Pure BLE range extension |
| `led-desk.yaml` | WS2812B addressable LED strips |

Commit via PR — CI validates the config (`esphome config`) before merge.

## 2. First flash (USB, once per board)

1. Open the ESPHome dashboard (add-on) — the new config appears (see
   runbook 02 for how repo configs reach the add-on).
2. Connect the bare ESP32 to the machine running your browser via USB.
3. Board menu → **Install** → *Plug into this computer* (uses Web Serial;
   Chrome/Edge required).
4. After flashing, the board joins WiFi. **Reserve its IP** in the router.

## 3. Adopt in Home Assistant

Settings → Devices & Services → ESPHome device is discovered → Configure →
enter the API encryption key (from `secrets.yaml`). Entities appear with the
`friendly_name` prefix.

Then:
- Assign an Area.
- Expose relevant entities to Alexa (runbook 03).
- Wire it into `packages/` automations and `dashboards/overview.yaml` via PR.

## 4. Updates are OTA

Config changes: edit YAML → PR → merge → open ESPHome dashboard → **Install**
→ *Wirelessly*. No USB needed after first flash.

## Hardware notes

- Power PIRs (HC-SR501) from 5V/VIN, signal is 3.3V-safe.
- I2C default pins on classic ESP32: SDA=GPIO21, SCL=GPIO22.
- Avoid strapping pins GPIO0/2/12/15 for inputs; they affect boot.
- WS2812B strips: inject 5V power for >60 LEDs; a 330Ω resistor on data and
  a 1000µF cap across power prevent first-LED burnout.
- If a board can't reach WiFi it raises its own AP (`<device_name>`,
  password = `fallback_ap_password`) — connect to it to fix WiFi credentials.

Next: [06 — Backups](06-backups.md)
