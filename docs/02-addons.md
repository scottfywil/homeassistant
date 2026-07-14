# 02 — Install and Configure Add-ons

Install order matters: Mosquitto before Zigbee2MQTT.

All add-ons: Settings → Add-ons → Add-on Store. For each one below, enable
**Start on boot** and **Watchdog**.

## 1. Mosquitto broker (MQTT)

1. Install **Mosquitto broker** (Official apps), enable Start-on-boot +
   Watchdog, start it.
2. Settings → Devices & Services: the **MQTT** integration shows up as
   discovered — click Add/Submit. It connects through the add-on's internal
   auth; no credentials needed.
3. Optional (for external MQTT clients only): create a dedicated HA user
   matching `mqtt_username`/`mqtt_password` in `secrets.yaml`
   (Settings → People → Users; local-only, not admin, **lowercase username**
   — HA rejects mixed case). The add-ons below do NOT need it.

## 2. Zigbee2MQTT

1. Plug the MG24 dongle **on the USB extension cable**, into a rear USB-A port.
2. HA will auto-discover the dongle as a ZHA integration — **Ignore** that
   discovery (Settings → Devices & Services → Discovered → Ignore); ZHA and
   Zigbee2MQTT can't share the radio, and this build uses Z2M.
3. App store → ⋮ → Repositories → add
   `https://github.com/zigbee2mqtt/hassio-zigbee2mqtt`, then install
   **Zigbee2MQTT**. Enable Start-on-boot + Watchdog + Show in sidebar.
4. Pre-seed the data config from the SSH terminal (channel, frontend — see
   [zigbee2mqtt-reference.yaml](zigbee2mqtt-reference.yaml)):
   ```bash
   mkdir -p /config/zigbee2mqtt
   # write homeassistant/frontend/permit_join/advanced keys per the reference
   ```
5. In the add-on **Configuration** tab: leave `mqtt` **entirely blank**
   (the add-on auto-authenticates to Mosquitto via Supervisor service
   credentials — no MQTT user needed). Under `serial`, set `port` to the
   stable path (find it: `ls -l /dev/serial/by-id/` — the MG24 shows as
   `usb-SONOFF_SONOFF_Dongle_Plus_MG24_...-if00-port0`, enumerating as
   ttyUSB0) and `adapter: ember`. Save.
6. Start. The Log should show `[STACK STATUS] Network up`, coordinator
   `EmberZNet 7.4.5`, `Connected to MQTT server`, `Zigbee2MQTT started!`.
7. `permit_join` stays off until pairing (runbook 04).

## 3. ESPHome

1. Install **ESPHome Device Builder** (Official), Start-on-boot + Watchdog +
   sidebar, start.
2. The add-on reads YAMLs from its own config dir, not `/config`. Symlink the
   repo's files in from the SSH terminal — targets use `/homeassistant/...`
   because that's the repo's path *inside the ESPHome container*:
   ```bash
   cd /addon_configs/5c53de3b_esphome
   ln -sfn /homeassistant/esphome/common common
   for f in /config/esphome/*.yaml; do ln -sf "/homeassistant/esphome/$(basename "$f")" .; done
   rm -f secrets.yaml && ln -s /homeassistant/secrets.yaml secrets.yaml
   ```
   New boards added to the repo need one new `ln -sf` (or rerun the loop).
3. The boards from `esphome/` appear in the dashboard, ready to build.
   First flash per board is over USB; after that it's OTA (runbook 05).

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
