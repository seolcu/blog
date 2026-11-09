---
title: "Hostveil — guided security hardening for self-hosted Linux servers"
summary: "Single Go binary that scans a self-hosted Linux server (SSH, firewall, Docker/Compose, updates, exposed ports, CVEs), gives a 0–100 score, explains each finding in plain language, and applies fixes with preview, backup and one-command rollback. Includes a TUI and a web dashboard."
date: 2026-11-09
status: active
verified_at: 2026-11-09
verified_how: "Summary checked against the repository README on 2026-11-09. Tested environments are those the README states."
repo: "https://github.com/seolcu/hostveil"
homepage: "https://hostveil.seolcu.com/"
license: "GPL-3.0"
applies_to:
  latest release: "v3.35.0 (2026-10-20)"
  targets: "self-hosted Linux servers, Docker / Docker Compose stacks"
keywords:
  - "self-hosted server hardening tool"
  - "docker compose security scan"
  - "homelab security audit"
  - "ssh hardening rollback"
---

## What it solves

Most self-hosted boxes run with whatever defaults the install left behind. Hostveil checks the high-impact areas, scores the host, and offers fixes. Every change is previewed and backed up, and file changes can be rolled back. No config file and no cloud account are needed.

## Measured effect

On a 2026-09-11 rerun, an Ubuntu VM was deliberately weakened (Nextcloud + PostgreSQL, Jellyfin + Redis, Portainer + Watchtower, root SSH login allowed, firewall and automatic updates off). Results after applying the Auto and Review fixes:

| Measured by | Before | After |
|---|---|---|
| Ports answering from the Docker bridge | 6 | 1 |
| CIS Docker Benchmark (pass / warn) | 17 / 15 | 20 / 12 |
| Lynis hardening index | 57 | 79 |

Grand Prize (Development), 2026-1 Ajou University SoftCon. Docs: <https://hostveil.seolcu.com/docs/>.
