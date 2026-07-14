# 01 — Flash Home Assistant OS and Onboard

## Hardware

Host: **HP EliteDesk 800 G3 Desktop Mini** (512 GB), running HAOS bare-metal.
HAOS takes over the entire disk, so **Windows is wiped** — this box has no
other job.

Also needed:

- **"Zigbee 3.0 USB Dongle Plus" MG24** (Silicon Labs EFR32MG24) Zigbee
  coordinator + a **USB 2.0 extension cable** (mandatory — moves the radio
  away from the PC's USB3/RF interference; plug the dongle into a rear
  **USB-A** port via the cable, not directly).
- **Wired Ethernet** into the EliteDesk's RJ45 port.
- The prepared **Ventoy USB stick** (≥8 GB): boots Ubuntu live AND carries the
  HAOS image as a file — one stick does both jobs. (Build it with Ventoy on
  any machine: install Ventoy to the stick, then copy the Ubuntu desktop ISO
  and the `haos_generic-x86-64-*.img.xz` onto it as plain files.)
- USB keyboard + a monitor (DisplayPort or VGA — the G3 DM has both) for the
  BIOS steps.

> **Warning:** flashing wipes the target disk completely, including Windows and
> the recovery partition. There is no undo. The EliteDesk has a single internal
> drive (M.2 NVMe or 2.5" SATA depending on config); that is the target.

## Prep the EliteDesk BIOS

1. Power on and tap **Esc** (or **F10**) repeatedly to enter BIOS Setup.
2. **Advanced → Secure Boot Configuration** → set **Secure Boot** to
   *Disable*, and enable **Legacy Support** only if UEFI boot of the USB
   fails (prefer leaving it UEFI).
3. **Advanced → Boot Options** → confirm **USB boot** is enabled.
4. Save & Exit (**F10**).

## Flash

1. Insert the Ventoy USB into the EliteDesk, power on, and tap **F9** to open
   the one-time boot menu → choose the USB stick → pick the **Ubuntu** ISO in
   the Ventoy menu → **"Try Ubuntu"** (no install needed).
2. Open a terminal and get the HAOS image. **Field note:** Ventoy holds its
   exFAT partition locked while serving the ISO, so mounting it from the live
   session usually fails ("already mounted or mount point busy"). Don't
   fight it — just download the image over Ethernet instead:
   ```bash
   cd /tmp
   wget https://github.com/home-assistant/operating-system/releases/download/18.1/haos_generic-x86-64-18.1.img.xz
   ```
   (Check for a newer release; curl is not on the Ubuntu live image, wget is.
   If you must use the stick's copy, `sudo mount -o ro /dev/sdX1 /mnt` works
   only when Ventoy hasn't dm-mapped the partition.)
3. Identify the internal disk with `lsblk` — on the G3 DM it's `/dev/nvme0n1`
   (M.2 NVMe) or `/dev/sda` (2.5" SATA SSD). Confirm the ~512 GB size matches.
4. Write the image directly to that disk (substitute your real device):
   ```bash
   xzcat haos_generic-x86-64-*.img.xz | sudo dd of=/dev/nvme0n1 bs=4M status=progress
   ```
5. Power off, remove the USB stick, plug in the Zigbee dongle (via the USB
   extension cable) and Ethernet, then power on. Tap **F9** and boot the
   internal disk (or set it first in BIOS boot order via F10).

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
