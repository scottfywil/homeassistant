# 12 — Frigate NVR on a dedicated box

**Status: DECIDED 2026-09-02, NOT YET INSTALLED.** Every step below is still to do.

## Decision and why

Frigate runs on a **spare 9th-gen Intel Core i5 HP micro** (32 GB RAM, 512 GB NVMe,
Intel UHD 630 iGPU) as a standalone Docker install on Ubuntu Server. Home Assistant stays on
the EliteDesk 800 G3 exactly as it is. Recordings go to an **NFS share on the QNAP
TS-653A**. Investigation numbers live in
[09-integrations-status.md](09-integrations-status.md) "Frigate NVR"; the short version:

- **Why not the G3 add-on:** it would have worked for one doorbell (i7-6700T idle, HD 530
  handles 2–4 cameras), but the owner plans **3–8 local cameras long term**. At that count a
  dedicated box keeps NVR load, disk writes, and reboots away from the box the household
  depends on.
- **Why not migrate HA to the 9th-gen box:** UHD 630 and HD 530 are the same iGPU
  architecture family with the same Frigate inference band (15–35 ms); the only upgrade is
  RAM, which fits the G3 too. Migration = an evening of downtime, re-homing the Zigbee
  dongle, re-verifying Tailscale/Nabu Casa/Git Pull, for no real gain.
- **Why no Coral / GPU:** Frigate docs no longer recommend the Coral for new installs
  (Google archived the repo 2026-04-19). OpenVINO on the UHD 630 covers up to ~8 low-to-
  moderate-activity cameras. Discrete GPUs are for 12+ cameras or heavy GenAI.

## Sizing at 8 cameras (the long-term ceiling)

| Resource | 1 doorbell today | 8 cameras later | Notes |
|---|---|---|---|
| Detection | trivial | ~8 × 5 fps detect, only while motion | UHD 630 ≈ 15–25 ms → 40–66 detections/s budget; detection only runs on motion so real load is far lower |
| Decode | 1 sub-stream | 8 sub-streams | QSV/VAAPI on the iGPU; main streams are copied to disk, not decoded |
| RAM | ~1.5 GB | ~4–6 GB (+ more for Frigate+ semantic search/GenAI) | 32 GB is plenty |
| Network | ~5 Mbps | ~40 Mbps | Fine on gigabit; consider a camera VLAN + PoE switch when cameras 2+ arrive |
| Storage, continuous 24/7 @ 4 Mbps | ~44 GB/day | ~350 GB/day | 2 TB = ~45 days (1 cam) or ~6 days (8 cams) — plan motion-only recording on most cameras, or grow the QNAP pool |

## Prerequisites (owner actions)

1. **QNAP health first.** HA shows the TS-653A self-reporting a *warning* status — open QTS,
   check Storage & Snapshots / disk SMART, and fix or replace before trusting it with recordings.
2. **QNAP NFS share.** Create a volume/folder `frigate` (~2 TB), enable **NFS** (Control Panel →
   Network & File Services → NFS service), and grant the Frigate box's IP read/write. Prefer NFS
   over SMB — Frigate handles NFS more reliably.
3. **Doorbell IP first, then RTSP.** The doorbell is on a **DHCP lease today (172.16.105.106
   as of 2026-09-02)** — owner will move it to a fixed/reserved address at the start of the
   install session. Do that *before* anything references it, then re-check the HA `reolink`
   config entry still connects (HA auto-discovered it by mDNS, so a changed IP may need the
   entry reconfigured). Then Reolink app → Front Door → Device Settings → device-info row →
   **Advanced Network Settings → Server Settings → enable RTSP and ONVIF.** HA box is
   172.16.105.160, same /24. Optional: set the main stream to *fluency-first* bitrate mode and
   *Interframe Space 1x* (Frigate's Reolink guidance).
4. **Static/reserved IP** for the Frigate box too, in the router's DHCP.
5. **MQTT credentials.** The Mosquitto add-on on HA is already running for Zigbee2MQTT
   ([02-addons.md](02-addons.md)). Create a dedicated `frigate` MQTT user in the Mosquitto
   add-on config (type it in the HA UI; never paste it into chat or a file).

## Install (on the 9th-gen box)

1. **OS:** **Ubuntu Server 24.04 LTS** (owner's choice), minimal install, OpenSSH server only,
   **do not** tick the Docker snap in the installer. Static IP via netplan. Enable
   unattended-upgrades (on by default on Ubuntu Server).
2. **Intel GPU:** `apt install intel-media-va-driver-non-free intel-gpu-tools vainfo` (Ubuntu
   ships it in *restricted*/*multiverse*, enabled by default on Server) and confirm `vainfo`
   lists H.264 decode; confirm `/dev/dri/renderD128` exists. Add the Docker user to the
   `render` and `video` groups.
3. **Docker:** install Docker Engine + compose plugin from **Docker's apt repo**, not the
   `docker.io` package or the snap — the snap's confinement breaks `/dev/dri` and NFS binds.
4. **NFS mount:** `apt install nfs-common`; mount the QNAP share at `/mnt/frigate` via
   `/etc/fstab` with `_netdev,nofail` so a NAS outage does not hang boot. Frigate's DB stays on
   the local NVMe (`/opt/frigate/config`), only `/media/frigate` maps to the share.
5. **Compose** (`/opt/frigate/docker-compose.yml`), using the standard
   `ghcr.io/blakeblackshear/frigate:stable` image (OpenVINO is built in):
   - `devices: /dev/dri/renderD128`, `shm_size` per the Frigate calculator (≥ 128 MB for 1 cam),
     `/opt/frigate/config:/config`, `/mnt/frigate:/media/frigate`, a tmpfs on `/tmp/cache`,
     ports 8971 (auth UI) and 8554/8555 (go2rtc), `restart: unless-stopped`.
   - Camera credentials go in the container **environment** (`FRIGATE_RTSP_USER`,
     `FRIGATE_RTSP_PASSWORD`) referenced as `{FRIGATE_RTSP_USER}` in config — never inline.
6. **Frigate `config.yml` starting point** (one camera):
   - `mqtt:` host = HA box IP, the dedicated `frigate` user.
   - `detectors: ov: {type: openvino, device: GPU}` (default SSDLite MobileNet v2 model).
   - `ffmpeg: hwaccel_args: preset-vaapi`.
   - `go2rtc:` Reolink **http-flv** main stream
     (`ffmpeg:http://<doorbell-ip>/flv?port=1935&app=bcs&stream=channel0_main.bcs&user=...&password=...#video=copy#audio=copy#audio=opus`)
     plus the RTSP sub stream `rtsp://...@<doorbell-ip>:554/h264Preview_01_sub` for detect
     (`<doorbell-ip>` = the fixed address assigned in Prerequisites step 3).
   - `cameras: front_door:` detect on the sub stream (~640×480 @ 5 fps), record from the go2rtc
     main restream; `record: enabled, retain days 7 mode motion; alerts/detections retain 30`.
     Continuous recording is optional and affordable at one camera on 2 TB — owner's call.
   - `objects: track: [person, package, car]` to start; zones after the first week of clips.
7. Start, open `https://<frigate-ip>:8971`, set the admin password in the UI, confirm the
   detector shows ~15–25 ms inference and the live view works.

## Wire it into Home Assistant (GitOps as usual)

1. **HACS → Frigate** integration; config flow points at `http://<frigate-ip>:5000` (or the
   authenticated 8971 URL). It creates `camera.front_door` (Frigate),
   `binary_sensor.front_door_person_occupancy`, event sensors, and media-browser access to clips.
2. Keep the existing Reolink integration — it still owns the doorbell button
   (`binary_sensor.front_door_visitor`) and the chimes. Frigate adds object events.
3. Follow-ups for `packages/`: a `person`-at-door notification separate from the button press;
   swap the emailed snapshot in `doorbell_alerts.yaml` to the Frigate snapshot API if it proves
   more reliable than the HLS-derived one.
4. Update [09-integrations-status.md](09-integrations-status.md) with the real entity IDs once
   live — verify before building on them, same as every other integration here.

## Backups

- Frigate config + DB: nightly `tar` of `/opt/frigate/config` to the QNAP (cron on the Frigate
  box). Recordings are not backed up — they are the retention window.
- Add the Frigate box to whatever patch/backup routine the household PCs use; it is a second
  Linux machine to keep alive.

## Growth path (cameras 2–8)

- Wired PoE cameras on a dedicated camera VLAN/SSID with no internet egress; give the Frigate
  box a leg on that VLAN (the HP micro has one NIC — a USB 2.5 GbE adapter or VLAN trunk works).
- Add cameras one at a time in `config.yml`; watch inference ms and `detect` CPU in the Frigate
  System page. If inference climbs past ~40 ms sustained with 8 cameras, the cheap fix is a
  newer Intel NUC-class box, not a GPU.
- Storage: switch most cameras to motion-only retention, or grow the QNAP pool; 8 cameras at
  4 Mbps continuous is ~350 GB/day.

Next: [09 — Integrations status](09-integrations-status.md) (record entity IDs once live).
