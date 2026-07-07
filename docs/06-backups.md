# 06 — Backups

Git holds the config, but **not**: the `.storage/` directory (integrations,
UI settings, OAuth tokens, entity registry), the history database, Zigbee
network state, or add-on data. Those need real backups.

## Automatic backups (HAOS built-in)

1. Settings → System → Backups → Configure automatic backups.
2. Schedule: **daily**, keep **7** copies.
3. Encryption on (record the key in your password manager — a backup without
   its key is garbage).

## Offload off the box

A backup on the same disk protects against nothing. Two options, use one:

- **Nabu Casa Cloud Backup**: already paying for it — enable in the backup
  settings; one encrypted copy stored offsite. Easiest.
- **Samba/network copy**: with the Samba add-on running, a scheduled job on
  another machine copies `\\homeassistant\backup\*.tar` weekly to a NAS or
  desktop that's itself backed up.

## What to verify quarterly

1. A recent backup exists and downloads.
2. You still have the encryption key.
3. Zigbee2MQTT coordinator backup: Z2M frontend → Settings → Tools →
   download coordinator backup (lets a replacement dongle keep the network).

## Restore procedure

- **Full box loss**: flash HAOS (runbook 01) → onboarding screen →
  "Restore from backup" → upload the latest full backup. Everything returns:
  config, `.storage/`, add-ons, Zigbee network.
- **Config-only mistake**: `git revert` the bad commit and push — Git Pull
  redeploys the fixed config within 5 minutes.
- **Single add-on**: restore just that add-on from a full backup
  (Settings → System → Backups → pick backup → partial restore).
