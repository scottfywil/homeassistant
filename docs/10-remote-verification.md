# 10 — Remote verification from a cloud Claude session

Claude Code sessions started from the web/mobile app run in an isolated cloud
container, not on your PC. That container **cannot see your LAN**:
`homeassistant.local:8123` doesn't resolve, and there's no browser attached to
drive the UI. So a cloud session can merge a config change but cannot confirm
the Git Pull add-on actually deployed it — it can only tell you what landed on
`main`. That gap is how a silently-failed deploy goes unnoticed.

This runbook closes it over **Tailscale**, which the box is already on.
Nabu Casa works too and is documented as a fallback at the end, but Tailscale
is the better option: the traffic stays on your tailnet, it doesn't depend on
the Nabu Casa subscription, and tailnet ACLs can restrict the container to one
host and one port — real scoping that an HA token can't provide by itself.

## What was verified

Measured in a cloud session on 2026-07-25, not assumed:

- `/dev/net/tun` exists and the session runs as root → a real TUN interface
  works; no userspace-networking fallback needed.
- The agent proxy's `noProxy` list already contains **`100.64.0.0/10`**, the
  Tailscale CGNAT range → traffic to tailnet IPs routes directly instead of
  through the proxy (which blocks most outbound HTTPS).
- `tailscaled` 1.80.2 reached the control plane through the proxy:
  `CONNECT ... controlplane.tailscale.com:443 → 200 Connection Established`.

**Not yet verified:** the data plane. A node that authenticates still has to
carry packets, either directly or via a DERP relay over HTTPS. DERP should
traverse the same proxy path that the control plane did, but nothing here
proves it until a node actually joins and an HTTP request to the box succeeds.
Treat the first successful `curl` as the real test.

## 1. Tailnet: auth key and ACL

In the Tailscale admin console → Settings → Keys → **Generate auth key**:

- **Ephemeral** — on. The container is destroyed after each session; ephemeral
  nodes remove themselves, so your device list doesn't fill with dead entries.
- **Pre-approved** — on (only matters if device approval is enabled on the
  tailnet). Without it the node joins but can't route until you approve it by
  hand, which defeats the point.
- **Reusable** — on. Every new session is a new node.
- **Tags** — `tag:claude-code`. The tag is what the ACL keys off; an untagged
  key gives the container your own user's access to the whole tailnet.

Then scope it in the ACL editor. Grant the tag exactly one destination:

```jsonc
{
  "tagOwners": {
    "tag:claude-code": ["autogroup:admin"],
  },
  "acls": [
    // ... existing rules ...
    {
      "action": "accept",
      "src":    ["tag:claude-code"],
      "dst":    ["<ha-host>:8123"],  // the HA node's name or tailnet IP
    },
  ],
}
```

That's the security boundary worth having: even a leaked key reaches only
port 8123 on one host, and only while a session is live.

Note the box's **MagicDNS name or tailnet IP** (`100.x.y.z`) while you're in
the console — the container needs it, and MagicDNS may not resolve there.

## 2. Home Assistant: token from a non-admin user

HA long-lived access tokens inherit the full permissions of the user who
created them — **there is no read-only token scope**. Don't mint one from your
admin account. Create a limited user:

1. Settings → People → Add person.
   - Name: `Claude Verify`
   - "Allow person to login" → on
   - **Local access only → off** (tailnet traffic arrives as a remote client)
   - **Administrator → off**
2. Log out, log in **as that user**, avatar (bottom left) → Security →
   Long-lived access tokens → **Create token**, named `claude-code-web`.
3. Copy it once — HA never shows it again.

**Understand what you're handing over.** A non-admin token still reaches the
REST API: it can read every entity's state and it *can* call services (turn
things on/off, set the thermostat). What it loses is the admin surface —
add-ons, users, integrations, config files, backups, the supervisor. That's the
meaningful reduction, but this is not a read-only credential. Treat it as
"can operate the house, can't reconfigure it," and only wire it up if you're
comfortable with that.

Never put the token in this repo. `secrets.yaml` is gitignored and lives only
on the box; the token belongs in the environment, below.

## 3. Environment variables

In the Claude Code web app → environment settings for this repo's environment
(docs: <https://code.claude.com/docs/en/claude-code-on-the-web>):

| Variable      | Value                                     |
| ------------- | ----------------------------------------- |
| `TS_AUTHKEY`  | the tagged ephemeral key from step 1      |
| `HA_BASE_URL` | `http://100.x.y.z:8123` (tailnet address) |
| `HA_TOKEN`    | the token from step 2                     |

`http://`, not `https://` — inside the tailnet the transport is already
encrypted and the box has no cert for its tailnet address.

No network-policy change is needed for the tailnet hop itself, since
`100.64.0.0/10` bypasses the proxy. The control plane
(`controlplane.tailscale.com`) already worked through it under the current
policy; if a future policy tightens further, that host and Tailscale's DERP
servers are what must stay reachable.

Environment variables apply to **new** sessions — a running one won't see them.

## 4. Bootstrap in the session

Tailscale isn't installed in the container, and the container is wiped between
sessions, so each session installs and joins. Roughly 30 seconds:

```bash
cd "$SCRATCHPAD"   # or any writable dir
curl -fsSL https://pkgs.tailscale.com/stable/tailscale_1.80.2_amd64.tgz -o ts.tgz
tar xzf ts.tgz && mv tailscale_*/tailscale tailscale_*/tailscaled .
(./tailscaled --state=ts.state --socket=ts.sock --tun=ts0 &)
sleep 2
./tailscale --socket=ts.sock up \
  --authkey="$TS_AUTHKEY" --hostname=claude-code-web --accept-routes
./tailscale --socket=ts.sock status   # should list the HA node
```

`--socket` and `--state` keep it self-contained in the scratchpad rather than
writing to system paths. If `tailscale up` hangs instead of returning, that's
the data-plane caveat from above — check `tsd.log` for DERP errors.

To make this automatic, put it in a **SessionStart hook** (see
[session-start-hook docs](https://code.claude.com/docs/en/claude-code-on-the-web))
guarded on `TS_AUTHKEY` being set, so sessions without the key skip it cleanly
rather than failing.

## 5. Verification recipes

Ping — proves tailnet, token, and HA all work together:

```bash
curl -sS -H "Authorization: Bearer $HA_TOKEN" "$HA_BASE_URL/api/"
# {"message":"API running."}
```

Confirm a specific automation deployed and is enabled:

```bash
curl -sS -H "Authorization: Bearer $HA_TOKEN" \
  "$HA_BASE_URL/api/states/automation.<entity_id>"
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

Entity existence proves *an* automation deployed, not *which commit*. For a
precise answer, add a template sensor whose state is a version string bumped in
every commit:

```yaml
# packages/system.yaml
template:
  - sensor:
      - name: "Config version"
        unique_id: config_version
        state: "2026-08-26.1"  # bump this in each commit
```

Then `GET /api/states/sensor.config_version` answers the question exactly. The
cost is remembering to bump it; skip it if you'd rather not.

## 6. Hygiene

- **Revoke the auth key** from the Tailscale console to cut off new sessions;
  existing ephemeral nodes disappear on their own when the container dies.
- **Revoke the HA token** from the `Claude Verify` user's Security tab —
  immediate, and breaks nothing else.
- Removing `TS_AUTHKEY` or `HA_TOKEN` from the environment is the fastest kill
  switch; sessions then simply lose the ability to check.
- Rotate either if it's ever pasted into a chat, a log, or a commit.
- Keep this doc credential-free. If someone later records a real key, token, or
  tailnet address here, that's a leak — those belong in environment settings
  only.

## Fallback: Nabu Casa

If Tailscale is unavailable, the Nabu Casa remote URL also reaches the box from
a cloud session. Same token from step 2; differences:

- `HA_BASE_URL` = `https://<random-id>.ui.nabu.casa` (Settings → Home
  Assistant Cloud → Remote Control), and no Tailscale bootstrap.
- **A network-policy change is required.** The default policy blocks it — a
  cloud session gets `000` from `ui.nabu.casa`. The environment's policy must
  permit outbound to `*.ui.nabu.casa`, or the variables are useless.
- **It depends on the subscription.** The Nabu Casa account was a trial
  expiring **2026-08-14** ([09](09-integrations-status.md)); if it lapsed,
  this path is already dead.
- No per-port scoping. The token's permissions are the only boundary — the
  whole HA API is exposed to anything holding it, with no ACL layer beneath.

Don't port-forward 8123 to the internet as a third option. Tailscale and the
Nabu Casa tunnel both exist so you don't have to.
