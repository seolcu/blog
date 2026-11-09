---
title: "Keep a Linux laptop running with the lid closed (systemd-logind HandleLidSwitch)"
summary: "Set `HandleLidSwitch=ignore`, `HandleLidSwitchExternalPower=ignore` and `HandleLidSwitchDocked=ignore` in a drop-in under `/etc/systemd/logind.conf.d/`, then reboot. Check with `systemd-analyze cat-config systemd/logind.conf`."
date: 2025-10-11
lastmod: 2026-11-09
aliases: ["/posts/laptop-disable-lid-switch/"]
status: working
verified_at: 2025-10-11
verified_how: "Headless laptop servers running systemd; closing the lid no longer suspended them."
applies_to:
  OS: "any Linux distribution using systemd-logind"
keywords:
  - "HandleLidSwitch=ignore"
  - "laptop server suspends when lid closed"
  - "logind.conf.d"
---

## Fix

Use a drop-in instead of editing `/etc/systemd/logind.conf`. Package updates may replace the main file, but they leave drop-ins alone:

```bash
sudo mkdir -p /etc/systemd/logind.conf.d
sudo tee /etc/systemd/logind.conf.d/10-lid-ignore.conf >/dev/null <<'EOF'
[Login]
HandleLidSwitch=ignore
HandleLidSwitchExternalPower=ignore
HandleLidSwitchDocked=ignore
EOF
sudo reboot
```

On a headless server, `sudo systemctl restart systemd-logind` also applies the change. On a machine with a graphical session, restarting logind can end that session, so reboot instead.

## Verify

```bash
systemd-analyze cat-config systemd/logind.conf | grep -i lid
```

Close the lid and check from another machine that the host still answers (`ping`, `ssh`).

## Notes

- The three keys cover running on battery, on AC power, and docked or with an external display. Set all three; otherwise the laptop still suspends in one of those states.
- A desktop environment can take its own lid-switch inhibitor while its session is active. A headless server is not affected.
