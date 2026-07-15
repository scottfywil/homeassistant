# 09 — Integrations Status (living doc)

Snapshot of what's actually running on the box. Update as integrations are
added. Last updated: **2026-07-15**.

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
| Govee (`govee_ble` + **govee2mqtt**) | 4 BLE + ~24 via bridge (~142 entities) | 4 local BLE temp/humidity sensors; full Govee account via the govee2mqtt add-on in **API-key mode**. See Govee note below |
| iBeacon Tracker | 4 | |
| HP LaserJet (IPP) | 1 | printer status |
| LG webOS TV (`webostv`) | 1 | 2025 OLED65 C5 @ 172.16.105.143 → device "Great Room TV", **Living Room** area (area renamed from Great Room 2026-07-14; TV device name left as-is). Full power/vol/app control. (Also still visible via Google Cast) |
| Plex Media Server (`plex`) | 1 server | "WilsonMedia" PMS on a PC @ **172.16.105.180** (libraries on Synology NAS01 @ .100). Local; linked via plex.tv (account has a 2nd shared server "JAKES-PC" — not added). `sensor.wilsonmedia` = active streams; per-client `media_player` entities appear dynamically when Plex clients play (or via "Scan clients"). Server device left unassigned (infra) |
| QNAP (TS-653A) | 1 (+36 disabled) | NAS monitoring, admin acct, host:8080 SSL off → Utility Room area. NAS self-reports "warning" status — check QTS |
| QHM-1134 LED BLE | 1 | RGB/W controller (`led_ble`) |
| Blink | 6 | cloud; cams Back/Front Yard, Living Room, Basement, Camper + sync module. Camper out of scope |
| Tuya / Smart Life | 11 | cloud; user-code flow. Mostly outdoor plugs/switches (see area notes) |
| Google Nest | 2 (6 entities) | Family Room thermostat → Living Room; Garage camera → Garage. SDM + Pub/Sub events enabled. See setup notes below |
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
  **Wyze ⚠️ installed but blocked** — see note below. **Govee ✅ done** (govee2mqtt, API-key mode).

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

### Govee (full ecosystem) note (WORKING via API-key mode, 2026-07-15)
- Full Govee account now in HA via **govee2mqtt** (`wez/govee2mqtt`, add-on **v2026.03.25**),
  on top of the 4 local `govee_ble` sensors. Config: temp scale **F**, MQTT **auto**
  (core-mosquitto), **Govee API key set**, **Start-on-boot + Watchdog ON**.
- **~24 new devices / ~142 Govee entities** discovered via the Govee **Platform API** (mostly
  thermo-hygrometers — humidors/cabinets/"Aging"/bathrooms/freezer — plus plugs, kettles, an
  Office TV Backlight, etc.). Published to HA over MQTT discovery.
- ⚠️ **Runs API-key-ONLY — account email/password were removed.** The account (undocumented
  API) login returns **status 454** (Govee backend change / app-version enforcement, breaks the
  email/password path for all users — [#682](https://github.com/wez/govee2mqtt/issues/682)/[#626](https://github.com/wez/govee2mqtt/issues/626)/[#622](https://github.com/wez/govee2mqtt/issues/622)) and **blocked startup even with the API key
  present** — govee2mqtt still attempts the undoc login if account creds exist. Clearing
  email/password → it uses the Platform API + LAN and starts clean.
- **Trade-off of API-key-only:** no IoT real-time push (status is polled) and no Tap-to-Run
  scenes. **To regain those:** re-add Govee email/password in the add-on config **once
  govee2mqtt ships a fix** for the 454 (watch for an add-on update; Auto-update is OFF).
- ✅ **Deduped + placed (2026-07-15):** disabled the **4 local `govee_ble` devices**
  (H5110/H5177/H5179) — covered by their friendly-named govee2mqtt twins. Assigned 22 Govee
  devices to rooms: the **cigar/humidor cluster (13) → Rec Room**; Office Desktop/Office
  Humidor/Office TV Backlight → **Office**; bath sensors → Basement Bath / Master Bathroom /
  Powder Room / Boys' Bathroom; Kitchen Sink + Kettle → Kitchen; **Freezer → Utility Room**.
  **HubWise Kettle** left unassigned — **confirmed work-site device** (like the Tuya HubWise
  ones), not at home. Devices have no icon field, so no
  device-level "logos" — Govee brand logo + entity type-icons are automatic.
- **Z-Wave** — ❌ **cancelled.** The only driver (Kwikset lock re-pair) is dead: the
  910/912 locks are the house locks (confirmed same as the old "892"), stay on Vivint,
  and were never on SmartThings; garage is MyQ. **No local Z-Wave devices remain**, so the
  PZG23 dongle / Z-Wave JS is not needed unless a future local Z-Wave device appears.
- **SmartThings hubs (×2)** — ✅ **retired 2026-07-14.** Confirmed empty (locks on Vivint,
  nothing else paired); removed from the Samsung/SmartThings account + factory-reset. Never
  integrated in HA, so no HA-side cleanup was needed.
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
  Lights → Front Yard · Humidifier → Master Bedroom · Sam's Light → Sam's Bedroom · Hunter's
  Light → Hunter's Bedroom · STITCH Power Strip → Office.
- **Blink:** Back Yard cam → Back Yard · Front Yard cam → Front Yard. (Living Room→Great
  Room, Basement→Rec Room were already set.)
- **Vivint (unmapped 3):** Mudroom Door → Mudroom · Backyard Camera → Back Yard ·
  Entrance Motion Detector → Entryway.
- Earlier: Nest thermostat → Living Room, Nest Garage cam → Garage.
- **Area renames 2026-07-14** (all applied via area registry, 0 devices orphaned):
  Great Room → **Living Room** (LG "Great Room TV" *device* name left as-is); Primary Bedroom
  → **Master Bedroom**; Primary Bath → **Master Bathroom**; Half Bath → **Powder Room**;
  Hall Bath → **Boys' Bathroom**; Mechanical → **Utility Room**; Bedroom 2 → **Hunter's
  Bedroom**; Bedroom 3 → **Sam's Bedroom**.
  - The Bedroom 2/3 rename revealed the earlier kids'-light mapping was inverted; corrected:
    **Sam's Light → Sam's Bedroom**, **Hunter's Light → Hunter's Bedroom**.

**Deliberately left unassigned:** HubWise Spotlights + West Entrance (Tuya work-site,
shared Smart Life acct), Blink Camper (out of scope) + Blink sync-module (infra), and all
HA system/add-on/service devices (hassio, sun, bluetooth, cast, mqtt, hacs meta, iBeacon
trackers, Hue Bridge).

**Govee area pass done 2026-07-15** (govee2mqtt): 23 assigned (Rec Room ×13 cigar/humidor,
Office ×3, Kitchen ×2, Freezer → Utility Room, + 4 bath/powder sensors). **HubWise Kettle**
left unassigned — confirmed work-site device (not at home).
**Still placeable — needs room info:** the QHM-1134 `led_ble` controller (×1) and the HP
LaserJet printer (×1).

**Duplicate-scan notes (not acted on — your call):** (a) two Vivint devices share the name
**"Front Door"** — the Kwikset *lock* + the door-open *sensor* (not a true dup; rename to
disambiguate if wanted). (b) The **LG TV** also appears via **Google Cast** (separate
`media_player`) — kept, since Cast enables casting apps while `webostv` gives power/vol/app
control.

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
- ✅ **Home Assistant Alexa skill enabled + linked** to the Nabu Casa account; discovery ran,
  all **19 devices found** in Alexa (2026-07-14).
- ✅ **De-duplicated Alexa sources:** the same devices were also being published by vendor
  skills (Smart Life/Tuya especially → 14 dup plugs). Disabled **all overlapping vendor
  smart-home skills** in Alexa so each device is seen **once, via Home Assistant** (the single
  control layer). **Exception: the Wyze skill is kept enabled** — HA-Wyze is parked on the TLS
  issue, so Wyze devices stay controllable via Wyze's own Alexa skill until HA-Wyze is fixed.
  (Govee's skill only exposed sensors — nothing controllable lost.)
- Note: **Assist** (local voice) still auto-exposes (75 entities) — local only, left as-is;
  trim later if desired.

## Not yet started

- ESP32 presence sensors — parts not yet ordered ([08-presence-sensors.md](08-presence-sensors.md)).
- Automations in `packages/` beyond the starter office-lighting example.
