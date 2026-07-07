# 04 — Pairing and Integrating Devices

## Naming convention

Everything follows `<room> <device>` friendly names → `<room>_<device>`
entity IDs (e.g. `light.office_desk_lamp`, `binary_sensor.hallway_motion`).
Consistent names keep automations readable and Alexa commands natural.

## Zigbee devices (Hue, Aqara, IKEA, SmartThings sensors…)

1. Open the Zigbee2MQTT web UI → **Permit join (all)** — 254 s window.
2. Put the device in pairing mode (usually: hold reset 5 s / power-cycle
   bulbs 5×; check the device manual on https://www.zigbee2mqtt.io/supported-devices/).
3. Watch the Z2M log; the device appears → **rename it immediately** in Z2M
   (this sets the HA entity IDs).
4. Turn permit join off when done.
5. Battery devices: pair them **in place**, not next to the coordinator —
   they don't re-route well.

Tip: mains-powered Zigbee devices (bulbs, plugs) are routers and strengthen
the mesh; add a few before the battery sensors.

## WiFi devices (Tuya, Kasa, Wyze…)

Settings → Devices & Services → Add Integration:

- **TP-Link Kasa**: native `tplink` integration, fully local, usually
  auto-discovered.
- **Tuya-based** (most no-name plugs/bulbs): official **Tuya** integration
  (cloud, needs a Tuya/Smart Life account). For local control later,
  **LocalTuya** via HACS — more setup, no cloud dependency.
- **Wyze**: limited official support; bulbs/plugs work via the **Wyze**
  integration with an API key. Wyze cameras are not first-class citizens —
  don't build automations around them.

## Cloud devices (Ring, Nest, ecobee…)

- **Ring**: `ring` integration — doorbell/motion events, alarm status.
- **Nest**: Google Device Access (one-time $5 fee) → `nest` integration.
- **ecobee**: `ecobee` integration with an API key from the ecobee developer
  portal.

These are configured through the UI (they store OAuth tokens in `.storage/`,
which is deliberately not in git). Document *which* integrations are active
here as they're added, so a rebuild has a checklist.

## After adding any device

1. Rename entities to match the naming convention.
2. Assign the device to an Area (rooms power Alexa groups and dashboards).
3. Decide whether to expose it to Alexa (runbook 03).
4. If an automation should use it, add it to a package in `packages/` via a
   PR — not in the UI editor — so it's in git.

Next: [05 — New ESP32 board](05-new-esp32-board.md)
