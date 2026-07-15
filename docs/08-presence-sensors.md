# 08 — Presence Sensors: Build Plan and BOM

Strategy: **DIY ESP32 multisensors with mmWave radar** in rooms where people
sit still; **cheap Zigbee PIR** in transit spaces; **humidity** drives the
bathrooms. mmWave (LD2410C) detects breathing-level micro-motion, so lights
stay on for a person reading in a chair — the thing PIR can't do.

## Tech per room

| Room | Sensor | Why |
|---|---|---|
| Office | DIY multisensor | Sit-still room; also drives office lighting automation |
| Living Room | DIY multisensor | Sit-still (TV) |
| Rec Room (basement) | DIY multisensor | Sit-still (TV/games) |
| Workout Room | DIY multisensor | Still-ish (floor work); temp alerting too |
| Primary Bedroom | DIY multisensor | Sleep presence enables "everyone asleep" scene |
| Kitchen/Dinette | DIY multisensor | Standing-still cooking; lux for under-cabinet lights |
| Bedrooms 2–3 | Zigbee PIR (or multisensor later) | Lower stakes |
| Hallways, Mudroom, Laundry, Garage entry | Zigbee PIR (Sonoff SNZB-03P / Aqara P1) | Transit — fast trigger matters, stillness doesn't |
| Bathrooms ×3 | Zigbee temp/humidity (e.g. Sonoff SNZB-02D) | Humidity spike = shower → fan automation |

## BOM — DIY multisensor (per unit)

| Part | Spec / notes | ~AliExpress | ~Amazon |
|---|---|---|---|
| ESP32 dev board | ESP32-WROOM-32 DevKit, 38-pin, USB-C preferred | $4 | $8 |
| LD2410C | HiLink 24 GHz mmWave, **C variant** (has BLE for HLKRadarTool app) | $5 | $9 |
| BME280 breakout | 3.3 V I2C (beware BMP280 fakes — must read humidity) | $4 | $7 |
| BH1750 breakout | I2C light sensor | $2 | $5 |
| AM312 mini PIR | 3.3 V logic, low false-trigger (skip HC-SR501) | $2 | $5 |
| USB power supply + cable | Any 5 V/1 A wart + USB cable | $3 | $6 |
| Enclosure | 3D print — STLs + parametric source in [`hardware/enclosure/`](../hardware/enclosure/) | $2 | $4 |
| Perfboard, headers, wire | consumables | $1 | $2 |
| **Total per room** | | **~$23** | **~$46** |

**Initial order suggestion (6 rooms + spares):** 7× ESP32, 7× LD2410C,
7× BME280, 7× BH1750, 7× AM312 — modules are cheap enough that one spare
of everything is worth it. AliExpress ≈ $160 total, Amazon ≈ $300.
Multi-packs (ESP32 3-packs, sensor 5-packs) close most of the Amazon gap.
Specific Amazon listings with links:
[`hardware/enclosure/BOM-amazon.md`](../hardware/enclosure/BOM-amazon.md).

Buy separately (Zigbee, no build): ~4× Sonoff SNZB-03P PIR (~$12 ea),
3× Sonoff SNZB-02D temp/humidity (~$13 ea).

## Wiring

All connections point-to-point on perfboard; ESP32 3V3 and GND rails shared.

| Module pin | ESP32 pin | Note |
|---|---|---|
| LD2410C VCC | VIN (5 V) | Radar wants 5 V; its UART logic is 3.3 V-safe |
| LD2410C GND | GND | |
| LD2410C TX | GPIO16 | ESP RX |
| LD2410C RX | GPIO17 | ESP TX |
| BME280 VIN | 3V3 | |
| BME280 SDA / SCL | GPIO21 / GPIO22 | Shared I2C bus |
| BH1750 VCC | 3V3 | |
| BH1750 SDA / SCL | GPIO21 / GPIO22 | Shared I2C bus |
| AM312 VCC | 3V3 | |
| AM312 OUT | GPIO27 | |

Enclosure notes: the LD2410C must face the room with **no metal** in front
of it (plastic is transparent to 24 GHz radar); give the BME280 vent slots
away from the ESP32 (its heat skews temperature ~1–2 °C in a sealed box);
BH1750 needs a light window or exterior mounting.

## Firmware

`esphome/office-sensor.yaml` is the canonical multisensor config —
LD2410C on UART2, radar tuning entities (timeout, gates) exposed to HA so
per-room tuning needs no reflash. Clone it per room (runbook 05):
change `device_name`/`friendly_name`, flash once over USB, OTA forever.

## Placement and tuning

- Mount in a **corner at 1.5–2 m height**, aimed across the room's seating.
- Radar sees through drywall — point it away from the neighboring room or
  reduce max gates until it stops.
- Keep it away from **ceiling fans, HVAC vents, and windows** (moving
  foliage) — the classic false-positive sources.
- Tune from HA: raise **Radar Timeout** (seconds of stillness before
  presence clears) to ~60–120 s in sit-still rooms; reduce **Max Gates**
  (each gate ≈ 0.75 m) until the sensor covers the room and nothing beyond.
- The LD2410**C**'s Bluetooth works with the HLKRadarTool phone app for
  per-gate sensitivity when HA-level tuning isn't enough.

## Automation pattern

PIR gives the **fast on** (sub-second); radar gives the **honest off**:

```yaml
# on:  PIR motion (instant)  |  off: radar presence clear for 5 min
triggers:
  - trigger: state
    entity_id: binary_sensor.office_sensor_motion
    to: "on"
```

See `packages/lighting.yaml` for the live office implementation.
