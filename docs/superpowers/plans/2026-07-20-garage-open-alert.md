# Garage-Open Overnight Alert Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Email Scott when either garage's contact sensor is open ≥10 continuous minutes between 22:00–05:00 (America/Chicago), plus an all-clear when it closes, per `docs/superpowers/specs/2026-07-19-garage-open-alert-design.md`.

**Architecture:** One self-contained package, `packages/garage_alerts.yaml`, following the existing `packages/lighting.yaml` style (modern `triggers:`/`conditions:`/`actions:` schema, `action:` not `service:`). Declares a new `notify: platform: smtp` entry (`notify.garage_alert_email`) plus two `input_boolean` flags and four explicit per-door automations (no templating/looping across doors, matching the planned cabinet package's style).

**Tech Stack:** Home Assistant YAML packages, SMTP2GO relay via the built-in `smtp` notify platform, GitHub Actions CI (yamllint + `frenck/action-home-assistant` config check), Git Pull add-on for GitOps deploy.

## Global Constraints

- Window: alert only fires 22:00:00–05:00:00 America/Chicago (HA `time` condition wraps midnight automatically when `before` < `after`).
- Threshold: 10 continuous minutes open (`for: "00:10:00"` on the trigger).
- Behavior: one open-alert + one all-clear per episode — no repeat reminders (YAGNI, per spec).
- Recipient: Scott only (`alert_email_scott`) — do not add the wife's address (that's the cabinet package's job).
- Entity IDs are real, verbatim, non-uniform (IEEE-slug for Dad, friendly slug for Mom) — do not "clean up" or rename them:
  - Dad: `binary_sensor.0xffffb40e0601d430_contact`
  - Mom: `binary_sensor.mom_garage_sensor_contact`
- Notifier name `notify.garage_alert_email` must stay distinct from the future cabinet package's notifier — do not reuse the name `alert_email`.
- Do not declare a `twilio:` integration block anywhere in this package — SMS is a `# TODO(TFV)` marker only, deferred until Twilio toll-free verification is approved (tracked in `docs/09-integrations-status.md`).
- No `cover.*` control, no auto-close, no camera snapshot, no repeat reminders (all explicitly out of scope in the spec).

**Testing note:** This is a configuration repo — validation replaces TDD. Local yamllint + a fresh secrets-key check stand in for "run the test"; CI (`ha-config` job) is the authoritative HA config check since Home Assistant core isn't installed locally. Task 2's step 5 is the local check; CI on the PR branch is the real gate before merge.

---

### Task 1: Add the missing secret placeholders

**Files:**
- Modify: `secrets.yaml.example`

The spec assumes `smtp2go_username`, `smtp2go_password`, `alert_sender`, `alert_email_scott` already exist in `secrets.yaml.example`. Verified 2026-07-20: **they don't** — the file currently only has WiFi/ESPHome/MQTT keys. CI does `cp secrets.yaml.example secrets.yaml` before the HA config check, so without this the `ha-config` CI job will fail on missing `!secret` references the moment the package references them.

- [ ] **Step 1: Append an email-alerts section to `secrets.yaml.example`**

Add after the existing `--- MQTT ---` block:

```yaml

# --- Email alerts (SMTP2GO) ---
smtp2go_username: "smtp2go-username-here"
smtp2go_password: "smtp2go-password-here"
alert_sender: "alerts@example.com"
alert_email_scott: "scott@example.com"
```

- [ ] **Step 2: Commit**

```bash
git add secrets.yaml.example
git commit -m "chore(secrets): add SMTP2GO/email-alert secret placeholders for garage alerts"
```

---

### Task 2: Create `packages/garage_alerts.yaml`

**Files:**
- Create: `packages/garage_alerts.yaml`

**Interfaces:**
- Consumes: `!secret smtp2go_username`, `!secret smtp2go_password`, `!secret alert_sender`, `!secret alert_email_scott` (added in Task 1); entity IDs `binary_sensor.0xffffb40e0601d430_contact`, `binary_sensor.mom_garage_sensor_contact`.
- Produces: `notify.garage_alert_email`, `input_boolean.garage_dad_alerted`, `input_boolean.garage_mom_alerted`, automations `garage_dad_open_overnight`, `garage_dad_closed_all_clear`, `garage_mom_open_overnight`, `garage_mom_closed_all_clear`.

- [ ] **Step 1: Write the package file**

```yaml
# Garage-open overnight alert. Email only for now; SMS drops in once Twilio
# TFV is approved (see docs/09-integrations-status.md, "Cabinet alerting").
# Distinct notifier name (garage_alert_email) so it won't collide with the
# cabinet package's notifier when that later merges.
notify:
  - name: garage_alert_email
    platform: smtp
    sender: !secret alert_sender
    recipient:
      - !secret alert_email_scott
    server: mail.smtp2go.com
    port: 587
    username: !secret smtp2go_username
    password: !secret smtp2go_password
    encryption: starttls

input_boolean:
  garage_dad_alerted:
    name: Garage Dad Alerted
    icon: mdi:garage-alert
  garage_mom_alerted:
    name: Garage Mom Alerted
    icon: mdi:garage-alert

automation:
  - alias: "Garage - Dad open too long (overnight)"
    id: garage_dad_open_overnight
    triggers:
      - trigger: state
        entity_id: binary_sensor.0xffffb40e0601d430_contact
        to: "on"
        for: "00:10:00"
    conditions:
      - condition: time
        after: "22:00:00"
        before: "05:00:00"
    actions:
      - action: notify.garage_alert_email
        data:
          title: "Garage Alert"
          message: >-
            Dad garage door has been open since
            {{ as_local(trigger.to_state.last_changed).strftime('%-I:%M %p') }}
            (10+ minutes).
      - action: input_boolean.turn_on
        target:
          entity_id: input_boolean.garage_dad_alerted
      # TODO(TFV): add a notify.alert_sms action here once Twilio toll-free
      # verification is approved — reuse the cabinet package's Twilio
      # notifier, do NOT declare a second `twilio:` block (it's a global key).

  - alias: "Garage - Dad closed all-clear"
    id: garage_dad_closed_all_clear
    triggers:
      - trigger: state
        entity_id: binary_sensor.0xffffb40e0601d430_contact
        to: "off"
    conditions:
      - condition: state
        entity_id: input_boolean.garage_dad_alerted
        state: "on"
    actions:
      - action: notify.garage_alert_email
        data:
          title: "Garage Alert - All Clear"
          message: "Dad garage door is now closed."
      - action: input_boolean.turn_off
        target:
          entity_id: input_boolean.garage_dad_alerted
      # TODO(TFV): add a notify.alert_sms all-clear action once Twilio TFV is approved.

  - alias: "Garage - Mom open too long (overnight)"
    id: garage_mom_open_overnight
    triggers:
      - trigger: state
        entity_id: binary_sensor.mom_garage_sensor_contact
        to: "on"
        for: "00:10:00"
    conditions:
      - condition: time
        after: "22:00:00"
        before: "05:00:00"
    actions:
      - action: notify.garage_alert_email
        data:
          title: "Garage Alert"
          message: >-
            Mom garage door has been open since
            {{ as_local(trigger.to_state.last_changed).strftime('%-I:%M %p') }}
            (10+ minutes).
      - action: input_boolean.turn_on
        target:
          entity_id: input_boolean.garage_mom_alerted
      # TODO(TFV): add a notify.alert_sms action here once Twilio toll-free
      # verification is approved — reuse the cabinet package's Twilio
      # notifier, do NOT declare a second `twilio:` block (it's a global key).

  - alias: "Garage - Mom closed all-clear"
    id: garage_mom_closed_all_clear
    triggers:
      - trigger: state
        entity_id: binary_sensor.mom_garage_sensor_contact
        to: "off"
    conditions:
      - condition: state
        entity_id: input_boolean.garage_mom_alerted
        state: "on"
    actions:
      - action: notify.garage_alert_email
        data:
          title: "Garage Alert - All Clear"
          message: "Mom garage door is now closed."
      - action: input_boolean.turn_off
        target:
          entity_id: input_boolean.garage_mom_alerted
      # TODO(TFV): add a notify.alert_sms all-clear action once Twilio TFV is approved.
```

- [ ] **Step 2: Confirm the SMTP2GO `server`/`port`/`encryption` values**

`mail.smtp2go.com` / `587` / `starttls` are SMTP2GO's standard published relay settings, but they aren't recorded anywhere in this repo (no prior YAML `notify:` block exists to copy from) and haven't been verified against this account. Flag to Scott before merge; if wrong, swap to whatever SMTP2GO's dashboard shows for this account (alternate ports: 2525, 8025, 465-SSL).

- [ ] **Step 3: Run yamllint locally**

Run: `pip install yamllint && yamllint packages/garage_alerts.yaml secrets.yaml.example`
Expected: exit 0, no output.

- [ ] **Step 4: Sanity-check every `!secret` reference resolves**

Run:
```bash
grep -oE '!secret [a-z0-9_]+' packages/garage_alerts.yaml | sort -u -k2 | while read -r _ key; do
  grep -q "^${key}:" secrets.yaml.example && echo "OK $key" || echo "MISSING $key"
done
```
Expected: `OK` for all four keys (`smtp2go_username`, `smtp2go_password`, `alert_sender`, `alert_email_scott`), no `MISSING` lines.

- [ ] **Step 5: Commit**

```bash
git add packages/garage_alerts.yaml
git commit -m "feat(garage): add overnight garage-open email alert package"
```

---

### Task 3: Land via branch → CI → merge → deploy verification

**Files:** none (delivery step, per the spec's "Delivery / verification" section)

- [ ] **Step 1: Push a short-lived branch and open CI**

```bash
git checkout -b garage-open-alert
git push -u origin garage-open-alert
```
Expected: GitHub Actions runs `yamllint`, `ha-config`, and `esphome` jobs on the branch/PR.

- [ ] **Step 2: Confirm all three CI jobs are green**

Check via `gh run list --branch garage-open-alert` / `gh run view <run-id>`, or the PR's checks tab.
Expected: `yamllint`, `Home Assistant config check`, `ESPHome config check` all pass. If `ha-config` fails on a missing secret, re-check Task 1's keys match exactly what Task 2 references.

- [ ] **Step 3: Merge to `main`**

Only after explicit user confirmation — merging triggers the Git Pull add-on's auto-deploy (~300s) to the live box, which is real household infrastructure.

- [ ] **Step 4: Post-deploy verification via HA API/UI**

Confirm all 6 new entities exist and resolve:
- `automation.garage_dad_open_overnight`, `automation.garage_dad_closed_all_clear`
- `automation.garage_mom_open_overnight`, `automation.garage_mom_closed_all_clear`
- `input_boolean.garage_dad_alerted`, `input_boolean.garage_mom_alerted`

Also confirm `notify.garage_alert_email` appears as a callable service (Developer Tools → Actions), and send one test notification (Developer Tools → Actions → `notify.garage_alert_email` with a static test message) to confirm the SMTP2GO credentials actually work end-to-end.

That static test does **not** exercise the Jinja template in the real automations (it only proves SMTP creds work). Separately render the actual template in Developer Tools → Template — `{{ as_local(states.binary_sensor.mom_garage_sensor_contact.last_changed).strftime('%-I:%M %p') }}` — and confirm it prints America/Chicago wall-clock time, not UTC, before trusting the automation for a real overnight alert. Better still, flip one sensor open for 10+ minutes during the 22:00–05:00 window (or temporarily widen the condition) and confirm the real automation fires with a correctly-localized time.

---

## Self-Review

- **Spec coverage:** helpers ✅ (Task 2), notifier ✅ (Task 2), 4 automations ✅ (Task 2), SMS `# TODO(TFV)` markers ✅ (Task 2), delivery/CI/merge/verification ✅ (Task 3), out-of-scope items respected (no `cover.*`, no repeat reminders, no auto-close/snapshot).
- **Gap found not in the original spec:** `secrets.yaml.example` was missing the keys the spec assumed already existed — added as Task 1 so CI doesn't break.
- **Open question carried into Task 2:** exact SMTP2GO server/port/encryption aren't recorded anywhere in-repo; using published defaults, flagged for confirmation before merge.
- **Correctness catch (advisor review):** original draft used `states.binary_sensor['0x...'].last_changed.strftime(...)`, which is UTC (not America/Chicago as the spec requires) and relies on a fragile dict-style accessor for a digit-leading object_id. Fixed to `as_local(trigger.to_state.last_changed).strftime(...)`, which is correct for both doors and doesn't touch the awkward entity_id. Task 3's verification step now explicitly renders the template (not just a static test notification) to catch this class of bug before trusting the overnight alert.
