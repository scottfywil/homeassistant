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
| Upper | Primary Bedroom, Primary Bath, Bedroom 2, Bedroom 3, Bedroom 4, Hall Bath |

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

Clone the templates in `esphome/devices/` (see runbook 05). Suggested
build-out order:

| Board | Template | Location / purpose |
|---|---|---|
| `garage-relay` | garage-relay.yaml | **Two relay channels + two reed sensors** — double door and single door. Extend the template to a second relay/sensor pair. |
| `ble-proxy-main` | ble-proxy-hallway.yaml | Main floor, central |
| `ble-proxy-upper` | ble-proxy-hallway.yaml | Upstairs hall landing |
| `mechanical-sensor` | office-sensor.yaml | Mechanical room: temp/humidity; add a water-leak sensor input (GPIO + probe) near the water heater/sump |
| `rec-room-sensor` | office-sensor.yaml | Basement rec room: temp/humidity/motion/lux |
| room sensors ×N | office-sensor.yaml | One per occupied room as needed: Great Room, Kitchen, Primary, bedrooms, workout room |

Bathroom humidity (shower → fan automation) targets: Primary Bath, Hall
Bath, Basement Bath — Zigbee temp/humidity sensors (e.g. Aqara/Sonoff) are
easier than ESP32 boards in bathrooms; wire the automation in
`packages/climate.yaml`.

## Existing devices to integrate

Fill in exact models during setup (runbook 04) and check them off:

- [ ] WiFi plugs/bulbs — brand(s): ____ → native integration or LocalTuya
- [ ] Smart thermostat — brand: ____ → Nest / ecobee / Honeywell integration
- [ ] Video doorbell / cameras — brand: ____ → Ring / Wyze integration (cloud)
- [ ] Smart lock(s) — brand: ____ → check native vs cloud integration
- [ ] Garage opener if already smart (e.g. MyQ) — note: MyQ blocks HA;
      prefer the `garage-relay` board wired to the opener terminals instead
- [ ] Echo devices — count and rooms: ____ (voice via Nabu Casa, runbook 03)

## Automation ideas grounded in this layout

Once sensors exist, these go in `packages/` (each is a small PR):

- Bath fans on humidity spike, off 20 min after normal (all 3 full baths)
- Garage doors: alert if either door open >10 min after 9pm; auto-close option
- Mechanical room: leak sensor → shut-off alert + critical notification
- Workout room: motion → lights + fan; temp alert if >78°F
- Basement rec room lights on motion when dark (clone of the office pattern)
- "Everyone upstairs asleep" (upper motion quiet + time) → whole-house off scene
