# 01 — Flash Home Assistant OS and Onboard

## Hardware

Either works; the N100 has more headroom:

| Option | Notes |
|---|---|
| **Intel N100 mini PC** (~$150) | Beelink/GMKtec class, 8–16 GB RAM, NVMe. Fanless models available. Best choice if cameras/Frigate are ever on the roadmap. |
| **Raspberry Pi 4/5** (4 GB+) | Use an SSD via USB3, **not** an SD card, for the database's sake. |

Also needed:

- **Sonoff ZBDongle-E** (Zigbee coordinator) + a **USB 2.0 extension cable**
  (mandatory — moves the radio away from USB3/board RF interference).
- Ethernet connection strongly preferred over WiFi.

## Flash

### Mini PC (x86-64)

1. Download the generic x86-64 HAOS image from https://www.home-assistant.io/installation/generic-x86-64/
2. Boot the mini PC from a Ubuntu live USB, then write the HAOS image
   directly to the internal disk:
   `zstdcat haos_generic-x86-64-*.img.zst | sudo dd of=/dev/nvme0n1 bs=4M status=progress`
   (double-check the target disk with `lsblk` first)
3. Ensure UEFI boot is enabled in BIOS, secure boot disabled.

### Raspberry Pi

1. Use Raspberry Pi Imager → "Other specific-purpose OS" → Home Assistant OS.
2. Write to the SSD, connect SSD to a blue USB3 port, boot.

## First boot and onboarding

1. Connect Ethernet and power. Wait ~5 minutes for first boot.
2. Browse to `http://homeassistant.local:8123` (or find its IP on the router).
3. Create the owner account.
4. Set home name, location, unit system, and time zone in onboarding —
   these live in HA's UI-managed storage, not in this repo.
5. **Reserve the box's IP** in the router's DHCP settings.

## Connect this repo (manual first pull)

The Git Pull add-on (runbook 02) automates updates, but seed the config once:

1. Install the **Advanced SSH & Web Terminal** add-on (disable Protection mode)
   or the **Samba** add-on.
2. From the HA terminal:
   ```bash
   cd /config
   git init -b main
   git remote add origin https://github.com/scottfywil/homeassistant.git
   git fetch origin
   git checkout -f main
   ```
3. Copy `secrets.yaml.example` to `/config/secrets.yaml` and fill in real values.
4. Settings → System → Restart. Verify the "Home Assistant started"
   notification appears — that automation comes from `packages/system.yaml`,
   proving the repo config loaded.

Next: [02 — Add-ons](02-addons.md)
