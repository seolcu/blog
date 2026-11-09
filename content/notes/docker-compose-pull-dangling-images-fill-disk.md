---
title: "Automatic `docker compose pull` updates slowly fill the disk with dangling images"
summary: "Each `docker compose pull` + `up -d` leaves the previous image untagged (dangling). Nothing removes it, so weekly auto-updates grow `/var/lib/containerd` without bound. Run `docker image prune --force --filter until=336h` after the post-update health check passes."
date: 2026-11-09
status: working
verified_at: 2026-11-09
verified_how: "Root cause of a full 232 GB root filesystem on an Ubuntu 24.04 home server on 2026-08-09; fix running in weekly update jobs since."
applies_to:
  OS: "Ubuntu 24.04 LTS"
  Docker: "Docker Engine with containerd image store, Compose v2"
keywords:
  - "no space left on device"
  - "/var/lib/containerd"
  - "dangling images"
  - "docker image prune until"
  - "docker compose pull disk full"
---

## Symptom

Services started crash-looping when the root filesystem reached 0 bytes free. In this case `/var/lib/containerd` held 21 GB of 20 dangling images, about 1.2 GB per service per week, accumulated over months of weekly unattended updates.

```bash
docker image ls --filter dangling=true
sudo du -sh /var/lib/containerd /var/lib/docker 2>/dev/null
```

## Cause

`docker compose pull` re-points the tag at the new image, and the old one becomes `<none>:<none>`. Compose and the Docker daemon never delete it automatically.

## Fix

Prune **after** the health check passes. Until then the previous image is your rollback target. Keep a window of two weeks:

```bash
docker compose pull
docker compose up -d
# ... wait for the health endpoint ...
docker image prune --force --filter "until=336h"
```

Make a prune failure non-fatal: log it and exit 0. A full disk is the problem the prune solves, so it should not turn an otherwise good update into a failure. Once the backlog is gone, `Total reclaimed space: 0B` is the normal steady state.

## Other things that filled the same disk

- systemd journal without a size cap: 4.1 GB. Set `SystemMaxUse=` in `/etc/systemd/journald.conf` or vacuum with `journalctl --vacuum-size=500M`.
- Backups pruned by age only: manual re-runs multiplied them. Also cap retention by count.

## Monitor free space

Every endpoint monitor stayed green until services were already failing; a TCP port check even stayed green through a crash loop. Push a "disk used %" heartbeat every 15 minutes (DOWN at 85% here) so you get a warning before services break.
