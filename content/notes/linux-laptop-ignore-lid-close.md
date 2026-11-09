---
title: "Keep a Linux laptop running with the lid closed (systemd-logind HandleLidSwitch)"
summary: "Set `HandleLidSwitch=ignore`, `HandleLidSwitchExternalPower=ignore` and `HandleLidSwitchDocked=ignore` in a drop-in under `/etc/systemd/logind.conf.d/`, then reboot. Check the effective config with `systemd-analyze cat-config systemd/logind.conf`."
date: 2025-10-11
lastmod: 2026-11-09
aliases: ["/posts/laptop-disable-lid-switch/"]
status: working
verified_at: 2026-11-09
verified_how: "Read back the effective logind config on an HP laptop that runs as a headless home server (Ubuntu 24.04, systemd 255.4-1ubuntu8.18) via a drop-in `/etc/systemd/logind.conf.d/99-homelab.conf`. The setting has been in use since 2025-10."
applies_to:
  OS: "any Linux distribution using systemd-logind; verified on Ubuntu 24.04 LTS"
  systemd: "drop-in directories supported for years; verified on 255"
keywords:
  - "HandleLidSwitch=ignore"
  - "laptop server suspends when lid closed"
  - "logind.conf.d"
---

## Fix

Use a drop-in instead of editing `/etc/systemd/logind.conf`. Package updates may replace the main file, but they leave drop-ins alone:

```bash
sudo mkdir -p /etc/systemd/logind.conf.d
sudo tee /etc/systemd/logind.conf.d/99-lid-ignore.conf >/dev/null <<'EOF'
[Login]
HandleLidSwitch=ignore
HandleLidSwitchExternalPower=ignore
HandleLidSwitchDocked=ignore
EOF
sudo reboot
```

On a headless server, `sudo systemctl restart systemd-logind` also applies the change. On a machine with a graphical session, restarting logind can end that session, so reboot instead.

## Verify

`systemd-analyze cat-config` prints every file in the order systemd reads it. A later file wins, so the drop-in must appear after anything that sets a different value:

```console
$ systemd-analyze cat-config systemd/logind.conf | grep -E '^# /|^HandleLid'
# /etc/systemd/logind.conf
# /etc/systemd/logind.conf.d/99-homelab.conf
HandleLidSwitch=ignore
HandleLidSwitchExternalPower=ignore
HandleLidSwitchDocked=ignore
# /usr/lib/systemd/logind.conf.d/unattended-upgrades-logind-maxdelay.conf
```

(Ubuntu's unattended-upgrades ships its own logind drop-in under `/usr/lib`. It does not touch the lid keys.)

Then close the lid and check from another machine that the host still answers (`ping`, `ssh`).

## Notes

- The three keys cover running on battery, on AC power, and docked or with an external display. Set all three; otherwise the laptop still suspends in one of those states.
- A desktop environment can take its own lid-switch inhibitor while its session is active. A headless server is not affected.
