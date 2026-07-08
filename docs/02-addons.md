# 02 — Install and Configure Add-ons

Install order matters: Mosquitto before Zigbee2MQTT.

All add-ons: Settings → Add-ons → Add-on Store. For each one below, enable
**Start on boot** and **Watchdog**.

## 1. Mosquitto broker (MQTT)

1. Install **Mosquitto broker**, start it.
2. Create a dedicated HA user for MQTT: Settings → People → Users → Add —
   username/password matching `mqtt_username`/`mqtt_password` in your
   `secrets.yaml`. (Local-only user, not admin.)
3. Settings → Devices & Services: the **MQTT** integration is discovered —
   configure it with that user.

## 2. Zigbee2MQTT

1. Plug the MG24 dongle **on the USB extension cable**, into a rear USB-A port.
2. Find the adapter path: Settings → System → Hardware → All Hardware → look
   for `ttyACM0`/`ttyUSB0`. Prefer the stable `/dev/serial/by-id/...` path.
3. Install **Zigbee2MQTT** (add repository
   `https://github.com/zigbee2mqtt/hassio-zigbee2mqtt` if not listed).
4. Before first start, apply the settings from this repo's
   `zigbee2mqtt/configuration.yaml` via the add-on Configuration tab
   (serial port, adapter `ember`, channel, MQTT credentials). The add-on
   stores its live config in its own data directory — this repo's copy is
   the reference; keep them in sync when you change settings.
5. Start. Open the Z2M web UI (sidebar) and confirm the coordinator is up.
6. Leave `permit_join` off until pairing (runbook 04).

## 3. ESPHome

1. Install **ESPHome Device Builder**, start, open the dashboard.
2. Point it at this repo's configs. The add-on's config directory is separate
   from `/config`; symlink the repo's ESPHome tree into it from the SSH add-on:
   ```bash
   # adjust the addon_configs slug to what exists on your box
   cd /addon_configs/5c53de3b_esphome
   ln -s /config/esphome/common common
   ln -s /config/esphome/devices/*.yaml .
   cp /config/secrets.yaml secrets.yaml
   ```
   (If symlinks misbehave, copy instead and treat the repo as the master.)
3. The four boards from `esphome/devices/` appear in the dashboard, ready to
   build. First flash per board is over USB; after that it's OTA (runbook 05).

## 4. Git Pull (auto-deploy)

1. Install **Git pull**.
2. Configuration:
   ```yaml
   repository: https://github.com/scottfywil/homeassistant.git
   git_branch: main
   git_remote: origin
   auto_restart: true
   git_prune: true
   repeat:
     active: true
     interval: 300
   ```
3. Start. Every 5 minutes it fetches `main`; if HA-relevant files changed it
   restarts HA. Push to GitHub → box updates itself.
4. For a private repo, use a GitHub fine-grained PAT (contents: read) in the
   repository URL, or switch to SSH with a deployment key.

## 5. Tailscale (admin access)

1. Install **Tailscale**, start it, open Web UI, authenticate to the tailnet.
2. The box joins as `homeassistant` — reachable at
   `http://homeassistant:8123` from any tailnet device, no port forwarding.

## 6. Studio Code Server + Samba (quality of life)

- **Studio Code Server**: VS Code in the browser, editing `/config` directly.
  Remember: the repo is the source of truth — commit changes, don't let the
  box drift.
- **Samba share**: exposes `/config` on the LAN; also used for backup offload
  (runbook 06).

Next: [03 — Nabu Casa + Alexa](03-nabu-casa-alexa.md)
