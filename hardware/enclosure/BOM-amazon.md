# Multisensor BOM — Amazon Sourcing

Purchasing sheet for the room multisensor
([docs/08-presence-sensors.md](../../docs/08-presence-sensors.md)).
Quantities sized for a **6–7 unit build** (6 sit-still rooms + a spare).

> Prices and links captured **July 2026**. ASINs get relisted and prices
> drift — verify before ordering. Links point at specific listings chosen for
> rating and fit, not endorsements; equivalent parts work.

## Parts

| Part | Listing | Price | Qty for 6–7 |
|---|---|---|---|
| ESP32 board | [6× ESP32-DevKitC 38-pin USB-C (ESP-32D)](https://www.amazon.com/dp/B0DSZBH9N9) · 4.4★ | $29.96 | one 6-pack + 1 spare |
| LD2410C mmWave | [3× HLK-LD2410C 24GHz](https://www.amazon.com/dp/B0F1F97422) · 4.4★ | $20.48 | two 3-packs |
| ↳ best-rated single | [1× LD2410C](https://www.amazon.com/dp/B0BXDLHHH2) · 4.8★ | $11.99 | — |
| BME280 (3.3 V) | [BME280 3.3 V, 1-pack](https://www.amazon.com/dp/B0GRRDXGH8) · 5.0★ | $9.99 | ×6–7 |
| ↳ economy 2-pack | [2× GY-BME280](https://www.amazon.com/dp/B0DHPCFXCK) · 4.6★ | $12.99 | ×3–4 |
| BH1750 (GY-302) | [3× HiLetgo BH1750](https://www.amazon.com/dp/B00M0F29OS) · 4.5★ | $7.49 | two 3-packs |
| AM312 PIR | [5× WWZMDiB AM312](https://www.amazon.com/dp/B0CCF52DVJ) · 4.1★ | $9.99 | one to two 5-packs |
| Jumper wires | [ELEGOO 120-pc Dupont kit](https://www.amazon.com/dp/B01EV70C78) · 4.8★ | $6.98 | one kit |
| Perfboard + headers | [174-pc double-sided perfboard kit](https://www.amazon.com/dp/B0D8VSYQCW) | $18.99 | one kit |
| USB power (central) | [6×A + 4×C charging station, 50 W](https://www.amazon.com/dp/B0DKMWYWB2) · 4.3★ | $19.99 | one |

**Approx. total for 6–7 sensors: ~$150–170.**

## Buy-it-right checklist

1. **ESP32 = 38-pin USB-C DevKitC.** The enclosure board pocket (55.2 × 29.2 mm,
   in `generate_enclosure.py`) is cut for this. Do **not** buy 30-pin boards —
   they won't seat.
2. **Confirm BME280, not BMP280.** The BMP variant has no humidity sensor,
   which breaks the bathroom/climate automations. Wire to 3V3 per the pinout
   in docs/08 (5 V-labeled GY-BME280 modules also run fine on 3V3).
3. **LD2410C specifically** — the C variant has the Bluetooth tuning radio
   (HLKRadarTool app). Don't substitute plain LD2410 or LD2410B.

Any 5 V phone charger powers a sensor (ESP32 + radar ≈ 0.5 A); the multi-port
station just tidies several sensors onto one outlet.

## Not on this list (buy separately, see docs/08)

- Zigbee PIR for transit spaces (Sonoff SNZB-03P) — pairs to Zigbee2MQTT.
- Zigbee temp/humidity for bathrooms (Sonoff SNZB-02D).
- Enclosure filament — print `base.stl` + `lid.stl` from this folder.
