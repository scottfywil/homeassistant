# 01 — Flash Home Assistant OS and Onboard

## Hardware

Host: a **dedicated always-on x86-64 PC** running HAOS bare-metal. HAOS takes
over the entire disk, so **Windows is wiped** — this box has no other job.

Also needed:

- **Sonoff ZBDongle-E** (Zigbee coordinator) + a **USB 2.0 extension cable**
  (mandatory — moves the radio away from USB3/case RF interference).
- **Wired Ethernet** strongly preferred over WiFi for the controller.
- A spare USB stick (≥2 GB) to boot a live Linux for flashing.

> **Warning:** flashing wipes the target disk completely. Back up anything on
> the PC first. If the PC has more than one drive, know exactly which one you
> mean to write to.

## Flash

1. Download the generic x86-64 HAOS image from
   https://www.home-assistant.io/installation/generic-x86-64/
   (the `haos_generic-x86-64-*.img.zst` file).
2. Boot the PC from a Ubuntu live USB ("Try Ubuntu", no install needed).
3. Identify the internal disk with `lsblk` — typically `/dev/nvme0n1` (NVMe)
   or `/dev/sda` (SATA SSD). Confirm the size matches the drive you intend.
4. Write the image directly to that disk (substitute your real device):
   ```bash
   zstdcat haos_generic-x86-64-*.img.zst | sudo dd of=/dev/nvme0n1 bs=4M status=progress
   ```
5. In BIOS/UEFI: enable **UEFI boot**, disable **Secure Boot**, and set the
   internal disk as the boot device. Power off the PC and remove the USB stick.
6. Boot from the internal disk.

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
