# 09 — Integrations Status (living doc)

Snapshot of what's actually running on the box. Update as integrations are
added. Last updated: **2026-07-14**.

## Platform state

- HAOS 18.1 / Core 2026.7.x on the EliteDesk 800 G3 DM, wired, IP reserved.
- Repo deployed to `/config` via **Git pull** add-on (polls `main` every 300s,
  auto-restart on) — GitOps loop is live.
- **Nabu Casa**: logged in and connected (Alexa link + remote).
- **Tailscale**: on the tailnet as `homeassistant` (100.92.73.69), key-expiry
  disabled.
- **Automatic backups**: daily, keep 7, encrypted.
- **Areas**: all 18 created across 3 floors (see [07-home-layout.md](07-home-layout.md)).
- **HACS** installed (v2.0.5) at `/config/custom_components/hacs`, authed to
  GitHub (`scottfywil`) via device flow. HACS + its managed integrations live on
  the box **outside GitOps** — `custom_components/` is gitignored, so the repo
  does not reproduce them (inherent, not a bug). See install note below.

## Add-ons running

Mosquitto · Zigbee2MQTT (MG24, network up, ch 20) · ESPHome Device Builder
(reads `/config/esphome` via symlinks) · Git pull · Tailscale · Terminal & SSH.

## Integrations configured ✅

| Integration | Devices | Notes |
|---|---|---|
| Philips Hue | 4 | via Hue Bridge (local) |
| Roborock | 2 | account-linked |
| Synology DSM (Nas01, .100) | 6 | admin-group account, port 5000, SSL off |
| OctoPrint — Prusa Mini (.141) | 1 | → Workout Room |
| OctoPrint — Prusa MK3S+ (.153) | 1 | → Workout Room |
| Govee Bluetooth | 4 | temp/humidity sensors |
| iBeacon Tracker | 4 | |
| HP LaserJet (IPP) | 1 | printer status |
| LG webOS TV (`webostv`) | 1 | 2025 OLED65 C5 @ 172.16.105.143 → "Great Room TV", Great Room area. Full power/vol/app control. (Also still visible via Google Cast) |
| QNAP (TS-653A) | 1 (+36 disabled) | NAS monitoring, admin acct, host:8080 SSL off → Mechanical area. NAS self-reports "warning" status — check QTS |
| QHM-1134 LED BLE | 1 | RGB/W controller (`led_ble`) |
| Blink | 6 | cloud; cams Back/Front Yard, Living Room, Basement, Camper + sync module. Camper out of scope |
| Tuya / Smart Life | 11 | cloud; user-code flow. Mostly outdoor plugs/switches (see area notes) |
| Google Nest | 2 (6 entities) | Family Room thermostat → Great Room; Garage camera → Garage. SDM + Pub/Sub events enabled. See setup notes below |
| Vivint (HACS: `natekspencer/ha-vivint`) | 17 (68 entities) | cloud; user/pass + MFA. **Read-only posture** (pro-monitored). Cameras, door/window + glass-break + motion sensors, 2 Kwikset locks, garage doors. Vivint pre-mapped some to Areas. See Vivint notes below |
| MQTT / Zigbee2MQTT Bridge | — | infra |

### Nest / Google Device Access setup (for the record)
- **Cloud Project ID**: `home-assistant-nest-502415` (GCP, owned by scottyfwil@gmail.com)
- **Device Access Project ID**: `33a00d05-b96f-42f0-b525-48c9c48da0de`
- **OAuth client**: "Home Assistant" (Web); redirect `https://my.home-assistant.io/redirect/oauth`
- **Pub/Sub topic**: `projects/home-assistant-nest-502415/topics/home-assistant-nest`; sub `home-assistant-nest-sub`
- OAuth consent screen **published to Production** (avoids 7-day token expiry).
- ⚠️ **Gotcha (cost us time):** the Device Access project + the $5 fee landed under the
  **wrong Google account** (`falconcuffy@gmail.com`) because the DAC console was opened
  with a bare URL that defaulted to authuser=0. Devices are owned by scottyfwil. Fixed by
  adding falconcuffy as an **admin member** of scottyfwil's Google Home (the "add developer
  email as a home member" the error suggested). **Lesson: force `?authuser=`/`/u/N/` on all
  Google consoles.** Nest now depends on falconcuffy remaining a home member.
- ⚠️ Don't reload/navigate the HA config-flow tab mid-OAuth — it orphans the flow (no entry
  created but flow stays "in progress", blocking retries). A Core restart clears a stuck flow.

### HACS install note (for the record)
- The official **"Get HACS" app** (repo `github.com/hacs/addons`) installed and
  ran but **silently did nothing** — no files, empty log. Recovered by the
  documented **manual method** in the Terminal add-on: downloaded the release
  asset `github.com/hacs/integration/releases/latest/download/hacs.zip` (18 MB,
  v2.0.5) and unzipped it into `/config/custom_components/hacs`, then Core
  restart → add the **HACS** integration → **GitHub device flow**
  (github.com/login/device, account `scottfywil`, authorize HACS).
- The `wget … | bash` one-liner is the other official path but got blocked as
  remote-code-exec; the zip method is equivalent and auditable.
- The spent **Get HACS** app can be uninstalled (one-shot downloader, no longer needed).

### Vivint notes (for the record)
- Community integration `natekspencer/ha-vivint` (in the **default HACS store**;
  no custom repo needed). Setup: HACS → download → Core restart → Add
  integration → Vivint → username/password + **MFA code**. Requires Internet (cloud).
- **Read-only posture is discipline, not a toggle** — the integration exposes an
  `alarm_control_panel` (arm/disarm) plus lock/garage/climate controls regardless.
  Rule: no arming/disarming automations; don't expose the alarm panel (or locks)
  to Alexa in the exposure pass.
- ⚠️ **Kwikset locks + garage doors come in via Vivint** (Front Door "Smart Code 910",
  Mudroom "Door Lock 912", Scott/Megan garage). They're Z-Wave devices paired to the
  **Vivint panel**. This changes the [07](07-home-layout.md) Z-Wave plan (item below):
  moving them to HA's own Z-Wave JS means **unpairing from the Vivint panel** (may
  disrupt Vivint monitoring). Decide keep-via-Vivint vs. go-local before pairing.
- ⚠️ **Possible Nest duplicate**: Vivint surfaced a "Family Room (Nest)" device;
  the Nest is already integrated directly. Disable the Vivint-side climate entity
  to avoid a duplicate.

## Pending — each needs a credential/account from the user

- **EISI-NAS01** (192.168.7.10, discovered) — parked; different subnet.
- **Cloud accounts** still to add: **Ring**, **Wyze**. (Tuya, Blink, Nest, Vivint ✅ done.)
- **Z-Wave** — awaiting the Sonoff Dongle-PZG23 purchase; then Z-Wave JS. **Note:**
  the Kwikset 892 locks + garage doors are **already available via Vivint** (paired
  to the Vivint panel) — going local means unpairing from Vivint first. Decide
  keep-via-Vivint vs. go-local before pairing (see Vivint notes above +
  [07-home-layout.md](07-home-layout.md)).

## Device → Area assignment

Printers assigned to Workout Room. **Most other devices are not yet assigned
to Areas** — needs room-by-room placement info from the user. Assign in bulk
via the device registry once placements are known.

Assigned so far: Nest thermostat → Great Room, Nest Garage cam → Garage. Blink
auto-picked a few (Living Room→Great Room, Basement→Rec Room).

Still needs placement from the user (fold into the area batch):
- **Tuya (11)**: Back Fountain, Patio, Front Outdoor Lights, Bar, STITCH Power
  Strip, Sam's Light, Hunter's Light, Humidifier, Outside House Lights, +2
  "HubWise" switches. Most are **outdoor** — no outdoor Area exists yet (create
  one, or park in Garage). "HubWise Spotlights/West Entrance" may be **work-site**
  devices pulled in via the shared Smart Life account — confirm before assigning.
- **Blink (6)**: Back Yard, Front Yard cams (outdoor); Camper cam out of scope.
- Sam's/Hunter's Light → likely Bedroom 2 / Bedroom 3 (kids' rooms) — confirm.

## Not yet started

- Alexa entity-exposure pass ([03-nabu-casa-alexa.md](03-nabu-casa-alexa.md)) —
  expose deliberately, not "all".
- ESP32 presence sensors — parts not yet ordered ([08-presence-sensors.md](08-presence-sensors.md)).
- Automations in `packages/` beyond the starter office-lighting example.
