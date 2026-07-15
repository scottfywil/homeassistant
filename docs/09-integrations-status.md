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
| Vivint (HACS: `natekspencer/ha-vivint`) | 13 active (of 17; 4 disabled) | cloud; user/pass + MFA. **Read-only posture** (pro-monitored). Alarm panel, 2 Kwikset locks, door/window + glass-break + motion sensors, cameras. Garage (×3) + duplicate Nest disabled — see Vivint notes below. Vivint pre-mapped some to Areas |
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
- **Kept on Vivint (by decision):** the alarm panel (`alarm_control_panel.wilson_home`),
  the **Kwikset locks** (`lock.front_door` "Smart Code 910", `lock.mudroom_door` "912"),
  door/window + glass-break + motion sensors, cameras. Locks **stay on Vivint** — they're
  tied to the monitored alarm, so **no local Z-Wave migration** (cancels the old item #5
  lock re-pair plan).
- **Dropped from HA (disabled via device registry, `disabled_by: user`, 2026-07-14):**
  - 3 garage devices — **Scott's Garage** (NGD00Z-4, was offline), **Megan Garage Door**,
    **Scott Garage Door**. The old Vivint Z-Wave garage controllers were **replaced by MyQ**
    and are no longer used via Vivint. (Ghost devices may still linger on the Vivint panel —
    remove at the source in the Vivint app if desired.)
  - **Family Room (Nest)** — duplicate of the directly-integrated Nest. Direct Nest
    thermostat (`climate.family_room_family_room`) is retained.
  - Vivint enabled device count: **13** (down from 17). Re-enable any via the device page.

## Pending — each needs a credential/account from the user

- **EISI-NAS01** (192.168.7.10, discovered) — parked; different subnet.
- **Cloud accounts**: Tuya, Blink, Nest, Vivint ✅ done. **Ring dropped** (no Ring).
  **Wyze ⚠️ installed but blocked** — see note below.

### Wyze note (blocked, parked 2026-07-14)
- Integration `SecKatie/ha-wyzeapi` (default HACS store, **v0.1.38**) installed; config
  entry created (email/password + developer **API Key + Key ID** all accepted — auth is fine).
- **Setup fails** with a TLS cert error on the first data call:
  `ClientConnectorCertificateError … CERTIFICATE_VERIFY_FAILED: unable to get local issuer
  certificate` → `api.wyzecam.com:443` (in `wyzeapy`). Integration mislabels it "network issues".
- **Not credentials, not the network:** `curl https://api.wyzecam.com/` **from the SSH add-on**
  verifies the cert fine (HTTP 403, `ssl_verify_result=0`). Failure is **specific to the Core
  container's Python SSL** (curl ran in a different container — exact mechanism unconfirmed).
  Box is on **Python 3.14** (bleeding-edge) → a `wyzeapy`-vs-3.14 SSL regression is a live suspect.
- **Entry disabled** (`Disabled by user`) to stop the retry loop; API key preserved — one-click
  **Enable** to retry once there's a fix.
- **To revisit later:** check for a newer ha-wyzeapi release / recent issues mentioning HAOS
  or Python 3.14; ground-truth the chain with `openssl s_client -showcerts api.wyzecam.com:443`
  from the **Core** container; cameras would need a separate `docker-wyze-bridge` regardless.
- **Z-Wave** — ❌ **cancelled.** The only driver (Kwikset lock re-pair) is dead: the
  910/912 locks are the house locks (confirmed same as the old "892"), stay on Vivint,
  and were never on SmartThings; garage is MyQ. **No local Z-Wave devices remain**, so the
  PZG23 dongle / Z-Wave JS is not needed unless a future local Z-Wave device appears.
- **SmartThings hubs (×2)** — now **unblocked for retirement** (locks confirmed on Vivint,
  not SmartThings). Inventory anything else still paired first (see [07](07-home-layout.md)).
- **Garage doors** — controlled by **MyQ** (replaced the old Vivint Z-Wave controllers,
  now disabled). **No cloud path** — HA's MyQ integration was removed in 2023.12 and
  Chamberlain blocks 3rd-party access. Local path if HA control wanted: **ratgdo** ESPHome
  board wired to the opener (= the `garage-relay` plan in [07](07-home-layout.md)). Needs
  hardware; undecided/parked.

## Device → Area assignment

**Tuya + Blink batch done 2026-07-14.** Created two new outdoor Areas **Back Yard** +
**Patio** (Front Yard already existed, from Vivint). Areas now total 24.

Assigned this batch:
- **Tuya:** Back Fountain → Back Yard · Patio → Patio · Bar → Patio (assumed the *patio*
  bar; there's also a Rec Room bar — move if wrong) · Front Outdoor Lights + Outside House
  Lights → Front Yard · Humidifier → Primary Bedroom · Sam's Light → Bedroom 2 · Hunter's
  Light → Bedroom 3 · STITCH Power Strip → Office.
- **Blink:** Back Yard cam → Back Yard · Front Yard cam → Front Yard. (Living Room→Great
  Room, Basement→Rec Room were already set.)
- **Vivint (unmapped 3):** Mudroom Door → Mudroom · Backyard Camera → Back Yard ·
  Entrance Motion Detector → Entryway.
- Earlier: Nest thermostat → Great Room, Nest Garage cam → Garage.

**Deliberately left unassigned:** HubWise Spotlights + West Entrance (Tuya work-site,
shared Smart Life acct), Blink Camper (out of scope) + Blink sync-module (infra), and all
HA system/add-on/service devices (hassio, sun, bluetooth, cast, mqtt, hacs meta, iBeacon
trackers, Hue Bridge).

**Still placeable — needs room info from user:** Govee temp/humidity sensors (×4, cryptic
`H51xx` names), the QHM-1134 `led_ble` controller (×1), and the HP LaserJet printer (×1).

## Alexa (Nabu Casa) exposure — done 2026-07-14

- Nabu Casa **Connected**; Alexa integration on; **auto-expose OFF** (per [03](03-nabu-casa-alexa.md)).
  ⚠️ Nabu Casa account is a **trial expiring 2026-08-14** (swi***@coursewareexperts.com) —
  Alexa stops working when it lapses unless subscribed.
- **19 entities deliberately exposed to Alexa** (`cloud.alexa`): 4 lights (Dresser Lamp,
  Dining Room Lamp, Dining, QHM-1134), Nest thermostat (Family Room), and 14 plugs (Back
  Fountain, Patio 1–4, Front Outdoor Lights, Bar, STITCH 1–4, Sam's, Hunter's, Outside
  House Lights).
- **Not exposed:** all sensors (motion/camera/temp/humidity/diagnostic), camera privacy +
  motion-detection toggles, Z2M permit-join, Roborock config switches, **HubWise Spotlights/
  West Entrance** (work-site), **Vivint locks + alarm** (read-only), the misclassified
  "Humidifier" light. Google Assistant left at 0.
- ⏳ **User step remaining:** activate the **Home Assistant skill in the Alexa app** (link the
  Nabu Casa account) and run discovery — until then Alexa can't see the exposed devices.
- Note: **Assist** (local voice) still auto-exposes (75 entities) — local only, left as-is;
  trim later if desired.

## Not yet started

- ESP32 presence sensors — parts not yet ordered ([08-presence-sensors.md](08-presence-sensors.md)).
- Automations in `packages/` beyond the starter office-lighting example.
