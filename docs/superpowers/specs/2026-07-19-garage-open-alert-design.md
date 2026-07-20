# Garage-open overnight alert — design (2026-07-19)

**Status:** Implemented (2026-07-20). See `docs/superpowers/plans/2026-07-20-garage-open-alert.md`
and `docs/09-integrations-status.md` ("Garage-open overnight alert" section) for delivery
details and live-verification results.

## Goal
Alert Scott by email if a garage door is left **open for ≥10 continuous minutes
between 22:00 and 05:00** (America/Chicago), with a follow-up "all-clear" when it
closes. SMS to be added later once Twilio TFV is approved.

## Context / findings (verified live via HA API 2026-07-19)
- **No garage-door opener entity exists** (`cover.*` count = 0; MyQ removed, no cloud
  path — see docs/09). Open/closed state comes from two **Zigbee contact sensors**:
  - Dad garage → `binary_sensor.0xffffb40e0601d430_contact` (device_class `door`, healthy)
  - Mom garage → `binary_sensor.mom_garage_sensor_contact` (device_class `door`, healthy)
  - `on` = open, `off` = closed. (Note the IEEE-vs-slug entity-id inconsistency, same as
    the cabinet sensors — real IDs used verbatim.)
- **Notification:** SMTP2GO email works today; all required secrets already exist on the
  box and in `secrets.yaml.example` (`smtp2go_username/password`, `alert_sender`,
  `alert_email_scott`) → no new secrets, no CI risk. Twilio SMS is pending TFV.

## Decisions (confirmed with user)
- Channel: **email now**, structured so **SMS drops in later**.
- Recipient: **Scott only** (`alert_email_scott`).
- Window **22:00–05:00**, threshold **10 min**, re-alert behavior **one alert + all-clear**.

## Design — package `packages/garage_alerts.yaml` (self-contained, deploys via GitOps)
- **Helpers:** `input_boolean.garage_dad_alerted`, `input_boolean.garage_mom_alerted`
  — record that an open-alert fired, so the all-clear only sends when relevant.
- **Notifier:** `notify.garage_alert_email` (SMTP2GO). Distinct name to avoid colliding
  with the cabinet package's `alert_email` when that later merges.
- **Automations:**
  1. `Garage - Dad open too long (overnight)` — trigger: Dad sensor `on` for `00:10:00`;
     condition: time `after 22:00:00 before 05:00:00` (HA wraps midnight); actions: email
     ("Dad garage open since …") + turn on `garage_dad_alerted`.
  2. `Garage - Dad closed all-clear` — trigger: Dad sensor → `off`; condition:
     `garage_dad_alerted` is `on`; actions: email ("Dad garage now closed") + turn off flag.
  3–4. Same pair for **Mom** (`mom_garage_sensor_contact` / `garage_mom_alerted`).
  - Explicit per-door automations (4 total) — no templating, maximally readable, matches
    the cabinet package's style.
- **SMS later:** each open/all-clear action block gets a `# TODO(TFV)` marker; when TFV is
  approved, add a `notify.alert_sms` action **reusing the cabinet package's Twilio notifier**
  (do NOT declare a second `twilio:` block — that key is global and would duplicate).

## Delivery / verification
- Land via a short-lived branch → CI (`Home Assistant config check`) must pass →
  merge to `main` → Git-pull deploys (~300s).
- Post-deploy verification via HA API: confirm the 4 `automation.*` + 2 `input_boolean.*`
  entities exist and the trigger entity IDs resolve.

## Out of scope (YAGNI)
- No repeat reminders between the first alert and the all-clear.
- No opener control (no `cover` entity exists).
- No auto-close, no camera snapshot attach (could add later).
