# 03 — Nabu Casa and Alexa

Nabu Casa (Home Assistant Cloud, $6.50/mo) provides the maintained Alexa
skill bridge and secure remote access, and funds HA development.

## Subscribe

1. Settings → Home Assistant Cloud → Sign up / log in.
2. Remote access toggle is optional (Tailscale already covers admin access);
   Alexa only needs the cloud link, not the public remote UI.

## Link Alexa

1. In the Alexa app: More → Skills & Games → search **Home Assistant** →
   Enable → log in with the Nabu Casa account.
2. Alexa runs discovery; exposed HA entities appear as devices.

## Entity exposure — be deliberate

Settings → Voice assistants → Expose. Default HA behavior exposes new
entities automatically — **turn that off** and expose explicitly:

- **Expose:** lights, switches/relays, scenes, locks (consider PIN),
  thermostats, the LED strip, garage relay.
- **Don't expose:** diagnostic sensors (WiFi signal, uptime, IP), motion
  sensors you don't voice-query, anything you'd rather not control by voice.

Naming: Alexa matches on the entity's friendly name. Keep names short,
unique, and speakable — "Garage Relay" → "Alexa, turn on the garage relay".
Rename in HA (entity settings), not in the Alexa app, so one name rules both.

## Echo devices in HA (optional, later)

To have HA *control* the Echos (TTS announcements, volume, routines), add the
**Alexa Media Player** custom integration via HACS. Not required for voice
control of HA devices — skip until needed.

Next: [04 — Pairing devices](04-pairing-devices.md)
