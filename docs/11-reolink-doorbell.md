# 11 — Reolink Doorbell

Adding a Reolink WiFi video doorbell that's already joined to the home
network (paired once via the Reolink app, as all Reolink WiFi cameras
require for initial WiFi provisioning).

**✅ Live 2026-09-01.** HA auto-discovered it; the config flow only needed
the doorbell's local admin username/password, typed directly in the HA UI.
Model: **Reolink Video Doorbell WiFi (D340W)**. Real result, for the record
(see [09-integrations-status.md](09-integrations-status.md) "Reolink note"
for the full device/entity list): device **Front Door** → Area
**Entryway**; **`binary_sensor.front_door_visitor`** is the button-press
sensor to key a notification automation off. Two paired **Reolink Chime**
accessories came in on the same config entry → **Rec Room** ("Basement
Chime") and **Upstairs Hallway** ("Upstairs Chime", renamed from the
default "Reolink Chime").

## Why the native integration, not HACS

HA ships a **built-in `reolink` integration** (local push, no cloud, no
add-on, no HACS) that supports Reolink doorbells directly — video stream,
two-way talk, the doorbell-press event, and AI person/vehicle/package
detection where the model supports it. This is the same pattern as the
existing local integrations in this repo (Hue, `webostv`, Synology) rather
than the cloud pattern (Vivint, Nest, Tuya) — no account, no OAuth.

## Prerequisites

- Doorbell already provisioned onto WiFi via the **Reolink app** (done).
- **Same LAN/VLAN as the HA box.** If the network segments IoT devices onto
  a separate VLAN/SSID (not currently the case per [07](07-home-layout.md),
  but check), the integration needs the HA box to reach the doorbell's IP —
  open that path first.
- The doorbell's **admin username and password** (set during app
  provisioning) — needed once, typed directly into the HA config-flow form.
  **Type this yourself in the HA UI; don't paste it into chat/a file.**
- Optional but recommended first: open the doorbell in the Reolink app →
  check for a firmware update → apply it. The HA integration tracks
  upstream Reolink firmware fairly closely; an old firmware is the most
  common cause of a failed or partial config flow.
- Know the doorbell's **local IP** (check your router's client list or the
  Reolink app's device info) in case HA's auto-discovery doesn't surface it.

## Steps

1. **Settings → Devices & Services → Add Integration** → search **"Reolink"**.
   - If HA already discovered it (mDNS/UPnP), a **Reolink** card may already
     be sitting under "Discovered" at the top of the Devices & Services
     page — click **Configure** on that instead of starting a fresh search.
2. Enter the doorbell's **host/IP**, then its **admin username + password**.
   - Use **HTTPS** if the doorbell has it enabled in the Reolink app
     (Settings → Network → Advanced); otherwise HTTP is fine on a trusted
     LAN. Leave "Use HTTPS" off if you get a cert-verification failure and
     haven't set up a real cert on the camera.
3. Submit. HA should report the model, then create the device with these
   typical entities (exact names carry a device-name prefix HA generates
   from the doorbell's own name — confirm the real IDs after adding, the
   same "verify before you build on it" lesson as every other integration
   in [09](09-integrations-status.md)):
   - `camera.<name>` — live stream (sub/main stream selectable in options).
   - `binary_sensor.<name>_visitor` — **fires on doorbell button press**
     (this is the one to hang a notification automation off).
   - `binary_sensor.<name>_motion` (+ `_person`/`_vehicle`/`_package` if the
     model supports AI detection).
   - `switch.<name>_*` — IR lights, floodlight/spotlight if the model has
     one, and doorbell-specific toggles (e.g. visitor-button chime tone).
   - A **two-way-talk** `media_player.<name>` if the model supports it.
   - If a **Reolink Chime** is paired to the doorbell, it shows up as its
     own device with a "press" event of its own.
4. **Assign the device to an Area.** Confirm which door it's actually
   mounted at — likely **Front Yard** or **Entryway** given the existing
   Areas in [07-home-layout.md](07-home-layout.md), but don't assume; check
   against the physical install.
5. Rename entities to the `<room> <device>` convention (runbook 04) once
   the real entity IDs are confirmed.
6. Decide Alexa exposure (runbook 03) — likely **not exposed** at first,
   consistent with how Vivint/Blink cameras and motion sensors are handled
   (camera streams and press/motion events stay HA-side, not Alexa).

## After it's live: automation ideas

**✅ Built + live-tested 2026-09-01** — `packages/doorbell_alerts.yaml` sends
email (Scott + Megan, via the existing SMTP config entry) and SMS (existing
Twilio `notify.alert_sms`) when `binary_sensor.front_door_visitor` fires.
No new secrets needed. Verified with a real doorbell press — both channels
received.

Possible follow-ups, not built: attaching a camera snapshot to the
notification (`camera.snapshot` service, since Reolink's push includes a
still image), or a mobile-app push if the HA Companion app gets installed.

## Gotchas

- **The config flow needs the doorbell reachable from the HA box's
  network**, not from wherever you're driving the HA UI from — if HA and
  the doorbell are genuinely on different subnets, the add fails even
  though the Reolink app (phone, different network path) sees the doorbell
  fine.
- If the config flow reports an **authentication error** despite the
  password being correct, confirm you're not still using the doorbell's
  Reolink-cloud SIP-style credentials — the integration wants the
  **local admin login**, not the Reolink account email.

Next: [09 — Integrations status](09-integrations-status.md) (update once
this is live, same as every other integration added here).
