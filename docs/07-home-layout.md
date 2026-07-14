# 07 — Home Layout and Coverage Plan

Reference for Areas, radio coverage, and device placement. Street address
deliberately omitted — this repo is public.

## The house

- Two-story single-family, built 2005, ~2,700 sqft above grade
- Finished basement (~1,380 sqft)
- 3-stall attached garage, **two doors (double + single), both with openers**
- Gas furnace + central AC, gas fireplace in the great room
- HA server (EliteDesk) lives in the **basement mechanical/storage area**

## Areas by level

Create these in HA (Settings → Areas & Zones) and assign every device.
Areas power Alexa groups ("turn off the basement lights") and dashboards.

| Level | Areas |
|---|---|
| Basement | Rec Room, Workout Room, Basement Bath, Mechanical |
| Main | Kitchen, Dinette, Great Room, Dining Room, Half Bath, Laundry, Mudroom, Garage |
| Upper | Primary Bedroom, Primary Bath, Bedroom 2, Bedroom 3, Office (bedroom 4), Hall Bath |

## Radio coverage plan

The Zigbee coordinator (MG24 on the EliteDesk) sits in the **basement** —
the worst radio position in the house. The mesh only works if each level has
mains-powered Zigbee **routers** (plugs, in-wall switches, bulbs — anything
not battery-powered). Add routers before battery devices.

| Level | Zigbee router (min) | ESP32 BLE proxy |
|---|---|---|
| Basement | coordinator + 1 plug (Rec Room) | covered by proxies above via floor, add if BLE devices live here |
| Main | 1–2 plugs/switches (Kitchen + Great Room) | 1 (central — Great Room or hallway) |
| Upper | 1 plug/switch (hallway or Primary) | 1 (hall landing) |
| Garage | 1 (the garage-relay board is WiFi, so add a Zigbee plug if pairing Zigbee there) | — |

Checkpoints: after adding routers, the Zigbee2MQTT map (frontend → Map)
should show battery devices linking through same-floor routers, not
straight to the coordinator.

## ESP32 board placement

Clone the templates in `esphome/` (see runbook 05). Suggested
build-out order:

| Board | Template | Location / purpose |
|---|---|---|
| `garage-relay` | garage-relay.yaml | **Two relay channels + two reed sensors** — double door and single door. Extend the template to a second relay/sensor pair. |
| `ble-proxy-main` | ble-proxy-hallway.yaml | Main floor, central |
| `ble-proxy-upper` | ble-proxy-hallway.yaml | Upstairs hall landing |
| `mechanical-sensor` | office-sensor.yaml | Mechanical room: temp/humidity; add a water-leak sensor input (GPIO + probe) near the water heater/sump |
| `rec-room-sensor` | office-sensor.yaml | Basement rec room: presence/climate/lux multisensor |
| room multisensors ×N | office-sensor.yaml | mmWave presence + climate per sit-still room — see [08-presence-sensors.md](08-presence-sensors.md) for the room plan and BOM |

Bathroom humidity (shower → fan automation) targets: Primary Bath, Hall
Bath, Basement Bath — Zigbee temp/humidity sensors (e.g. Aqara/Sonoff) are
easier than ESP32 boards in bathrooms; wire the automation in
`packages/climate.yaml`.

## Existing devices to integrate

Work through these during setup (runbook 04):

- [ ] **Wyze** plugs/bulbs → Wyze integration (API key). Wyze *cams* are
      Alexa-only for now — don't build automations on them.
- [ ] **Tuya / Smart Life** plugs/bulbs → official Tuya integration first;
      migrate to LocalTuya (HACS) later for local control.
- [ ] **Philips Hue** — bridge bulbs stay on the **Hue Bridge** (local HA
      integration, excellent). Bulbs paired directly to an **Echo's Zigbee**
      get re-paired to Zigbee2MQTT (Echo loses direct pairing; voice keeps
      working via Nabu Casa).
- [ ] **Nest thermostat** → Google Device Access (one-time $5 developer
      registration); same project also covers Nest cameras/doorbell.
- [ ] **Cameras**: Ring → `ring` integration (events/motion, cloud);
      Nest → same Device Access project as thermostat; Blink → `blink`
      integration (cloud); Wyze cams → skip (above).
- [x] **Door locks** — the front-door and mudroom Kwikset locks come in via **Vivint**
      (models "SmartCode 910" + "Door Lock 912"; the earlier "892" label was loose — same
      physical locks, confirmed 2026-07-14). By decision they **stay on Vivint** (tied to
      the monitored alarm). The Z-Wave-JS lock migration below is **cancelled**.
- [ ] **SmartThings hubs (×2)** → retire. The locks were the reason to keep them and are
      now confirmed on Vivint (not SmartThings), so the hubs are **unblocked for retirement**
      — just inventory anything else still paired first; the SmartThings cloud integration
      can bridge stragglers temporarily.
- [x] **Vivint security system + cameras** → `natekspencer/ha-vivint` via HACS (cloud),
      done 2026-07-14. Read-only posture (arming left alone). Garage controllers (old
      Vivint Z-Wave, now MyQ) and a duplicate Nest were disabled; locks/alarm/sensors kept.
      See [09-integrations-status.md](09-integrations-status.md).
- [ ] **Garage openers** — controlled by **MyQ** (replaced the old Vivint Z-Wave openers,
      now disabled in HA). **No cloud path:** HA's MyQ integration was removed in 2023.12
      and Chamberlain blocks third-party API access — do not pursue a cloud MyQ integration.
      **Local path = the plan:** wire a board to the opener control terminals. Recommended
      **[ratgdo](https://paulwieland.github.io/ratgdo/)** (purpose-built ESPHome board,
      Security+ 2.0 compatible, local control + status, MyQ app keeps working) — a
      productized version of the `garage-relay` board in the ESPHome table above. Needs
      hardware. Undecided whether to pursue.
- [ ] **LG webOS TV (2025, Living Room)** → `webostv` integration — local,
      power/volume/app control; great for "movie mode" scenes.
- [ ] **Fire TV devices (many)** → `androidtv` integration per device as
      wanted; not a priority.
- [ ] **eero Pro 7 mesh (×2)** — the network itself. No official HA
      integration; use the eero app for the DHCP reservations this project
      needs (HA box, every ESP32 board). Old eero 2nd-gens are retired.

## Echo fleet (voice endpoints via Nabu Casa)

Active in-home units and where they sit — these become the rooms where
voice control must work well (assign matching Alexa groups):

| Echo | Location |
|---|---|
| Echo 4th gen | Primary bedroom |
| Echo Dot 5th gen ×2 | Kids' bedrooms |
| Echo 4th gen | Basement rec room |
| Echo Dot 3rd gen | Workout room |
| Echo Dot | Garage |
| Echo Show 8 | Kitchen |
| Echo Show 5 | Office (bedroom 4, upstairs) |
| Echo 4th gen ("Red") | Great Room (main-level living room) |
| Echo Dot | Patio |
| Echo Dot 3rd gen | Outside bar |

Not in scope: two camper units, two work units, three retired/dead Dots.
An Echo's built-in Zigbee radio may currently host some Hue bulbs — those
re-pair to Zigbee2MQTT during setup (runbook 04).

## Z-Wave (locks)

> ❌ **Cancelled 2026-07-14.** The door locks come in via **Vivint** (SmartCode 910 + Door
> Lock 912 — same locks the plan loosely called "892") and, by decision, **stay on Vivint**
> (tied to the monitored alarm). Confirmed they are not on SmartThings. Garage doors are
> **not** part of this either (MyQ now, not Z-Wave). Net: no local Z-Wave devices remain —
> the **PZG23 dongle / Z-Wave JS is not needed** unless a genuinely local Z-Wave device
> turns up later. Section kept for historical rationale only.

The Kwikset 892s are Z-Wave — a third radio alongside WiFi and Zigbee.

**Radio: Sonoff Dongle-PZG23** (Silicon Labs EFR32ZG23, Z-Wave 800 series,
**US frequency / 908.42 MHz** — region-locked, EU variant won't work) +
the **Z-Wave JS** add-on. HA 2025.12.2+ auto-discovers the dongle.

Plan: exclude the locks from the SmartThings hub(s), pair them to Z-Wave JS
(892s are S0-only — fine for locks), then retire both SmartThings hubs.
No cloud in the lock path.

Notes:
- The 892 must be paired **within a few feet of the controller** (S0
  inclusion is low-power) — either carry the EliteDesk near the door once,
  or pair before final rack placement in the basement.
- Same placement rule as Zigbee: dongle on its USB extension cable
  (included), USB 2.0 port, and keep the Z-Wave and Zigbee dongles apart
  from each other. The adjustable external antenna helps reach the
  upstairs locks from the basement.

## Automation ideas grounded in this layout

Once sensors exist, these go in `packages/` (each is a small PR):

- Bath fans on humidity spike, off 20 min after normal (all 3 full baths)
- Garage doors: alert if either door open >10 min after 9pm; auto-close option
- Mechanical room: leak sensor → shut-off alert + critical notification
- Workout room: motion → lights + fan; temp alert if >78°F
- Basement rec room lights on motion when dark (clone of the office pattern)
- "Everyone upstairs asleep" (upper motion quiet + time) → whole-house off scene
