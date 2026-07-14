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
which is deliberately not in git). The live list of what's actually
configured lives in [09-integrations-status.md](09-integrations-status.md).

## NAS / server integrations

- **Synology DSM**: **requires an account in the `administrators` group** —
  a least-privilege read-only user does NOT work (the integration reads
  system/storage/utilization APIs that return "Insufficient user privilege"
  otherwise). In the Add dialog, match the port to the SSL setting:
  **port 5000 with "Uses an SSL certificate" unchecked** (plain HTTP), or
  **5001 with it checked** (HTTPS). Mismatched (5000 + SSL on) hangs silently
  with no error. Leave "Verify SSL certificate" off for a self-signed cert.
- **OctoPrint**: the config flow asks for your **OctoPrint username** (not an
  API key up front). After Submit, OctoPrint shows an **"Allow access"**
  prompt you approve in the printer's own web UI (Application Keys workflow).
  Host is auto-filled; port is usually **80** on an OctoPi image.
- **QNAP**: standard host + admin-ish account.

## Gotchas learned in the field (HA 2026.7.x)

- **HA usernames must be lowercase** — the Add User dialog silently rejects
  mixed case.
- **Password-manager autofill can leave a form's Submit button dead** — HA's
  form state doesn't see autofilled values. If Submit won't activate, clear
  the field and **type the value by hand**.
- The **Terminal add-on iframe** blocks direct URL navigation with an
  "unsaved changes" prompt — navigate via the HA sidebar instead.
- HA renamed "Add-ons" to **"Apps"** and there's no Advanced Mode gate.

## After adding any device

1. Rename entities to match the naming convention.
2. Assign the device to an Area (rooms power Alexa groups and dashboards).
3. Decide whether to expose it to Alexa (runbook 03).
4. If an automation should use it, add it to a package in `packages/` via a
   PR — not in the UI editor — so it's in git.

Next: [05 — New ESP32 board](05-new-esp32-board.md)
