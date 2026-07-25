# 10 — Remote verification from a cloud Claude session

Claude Code sessions started from the web/mobile app run in an isolated cloud
container, not on your PC. That container **cannot see your LAN**:
`homeassistant.local:8123` doesn't resolve, and there's no browser attached to
drive the UI. So a cloud session can merge a config change but cannot confirm
the Git Pull add-on actually deployed it — it can only tell you what landed on
`main`.

This runbook wires up read access so a cloud session can verify deploys itself.
Three pieces: a reachable URL, a token, and a network policy that allows the
traffic. All three are required; any one missing and the check fails.

## 1. Reachable URL (Nabu Casa)

Already paying for it (see [03](03-nabu-casa-alexa.md)).

1. Settings → Home Assistant Cloud → Remote Control.
2. Ensure remote access is **on** and copy the URL — it looks like
   `https://<random-id>.ui.nabu.casa`.

That hostname is the only ingress a cloud session can use. Don't port-forward
8123 to the internet as an alternative; the Nabu Casa tunnel exists precisely
so you don't have to.

⚠️ The Nabu Casa account is a **trial expiring 2026-08-14**
([09](09-integrations-status.md)). When it lapses, remote verification stops
working — that's the single point of failure here.

## 2. Token, minted from a dedicated non-admin user

Home Assistant long-lived access tokens (LLATs) inherit the full permissions of
the user who created them — **there is no read-only token scope**. So don't mint
one from your own admin account. Create a limited user instead:

1. Settings → People → Add person.
   - Name: `Claude Verify`
   - "Allow person to login" → on
   - **Advanced settings → Local access only → off** (it needs to come in over
     the Nabu Casa tunnel)
   - **Administrator → off**
2. Log out, log back in **as that user**, click the user avatar (bottom left) →
   Security tab → Long-lived access tokens → **Create token**. Name it
   `claude-code-web`.
3. Copy the token once — HA never shows it again.

**Understand what you're handing over.** A non-admin token still reaches the
REST API: it can read every entity's state and it *can* call services (turn
things on/off, set the thermostat). What it loses is the admin surface —
add-ons, users, integrations, config files, backups, the supervisor. That's the
meaningful reduction, but this is not a read-only credential. Treat it as
"can operate the house, can't reconfigure it," and only wire it up if you're
comfortable with that.

Never put the token in this repo. `secrets.yaml` is gitignored and lives only
on the box; the token belongs in the environment (next step), not in Git.

## 3. Environment: variables + network policy

In the Claude Code web app → environment settings for this repo's environment
(docs: <https://code.claude.com/docs/en/claude-code-on-the-web>):

- **Environment variables**
  - `HA_BASE_URL` = `https://<random-id>.ui.nabu.casa`
  - `HA_TOKEN` = the token from step 2
- **Network policy** — the default policy blocks general outbound HTTPS (a
  cloud session gets `000` from `ui.nabu.casa` today). Pick a policy that
  permits outbound to `*.ui.nabu.casa`, or add it to the allowlist if the
  policy supports one. Without this, the variables are useless.

Both apply to *new* sessions — an already-running session won't pick them up.

## 4. Verification recipes

Ping (proves URL + token + network policy all work):

```bash
curl -sS -H "Authorization: Bearer $HA_TOKEN" "$HA_BASE_URL/api/"
# {"message":"API running."}
```

Confirm a specific automation deployed and is enabled:

```bash
curl -sS -H "Authorization: Bearer $HA_TOKEN" \
  "$HA_BASE_URL/api/states/automation.climate_one_shot_72f_setpoint_2026_07_26"
# .state == "on"; .attributes.last_triggered shows if it has fired
```

Read a thermostat's current setpoint:

```bash
curl -sS -H "Authorization: Bearer $HA_TOKEN" \
  "$HA_BASE_URL/api/states/climate.family_room_family_room"
```

Timing: the Git Pull add-on redeploys within ~5 minutes of a push to `main`
([06](06-backups.md)), and a config reload has to follow before new automations
appear. If an entity 404s, wait a cycle and re-check before concluding the
deploy failed.

### Optional: a definitive "which commit is live" marker

Entity existence proves *an* automation deployed, not *which commit*. If you
want a precise answer, add a template sensor whose state is a version string
bumped in every commit:

```yaml
# packages/system.yaml
template:
  - sensor:
      - name: "Config version"
        unique_id: config_version
        state: "2026-07-26.1"  # bump this in each commit
```

Then `GET /api/states/sensor.config_version` answers the question exactly. The
cost is remembering to bump it; skip it if you'd rather not.

## 5. Hygiene

- Revoke the token any time from the `Claude Verify` user's Security tab —
  revocation is immediate and breaks nothing else.
- Rotate it if you ever paste it into a chat, a log, or a commit by accident.
- Removing `HA_TOKEN` from the environment is the fastest kill switch; the
  session simply loses the ability to check.
- Keep this doc token-free. If someone later records the actual URL or token
  here, that's a leak — they belong in the environment settings only.
